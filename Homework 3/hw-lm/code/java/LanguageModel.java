import java.io.*;
import java.util.*;
import java.util.regex.*;

/**
 * Language model superclass
 */
abstract class LanguageModel {
    Map<String, Integer> tokens;   // the c(...) function.
    ArrayList<String> tokenList;  // the training corpus stored as a list.  It starts with 2 BOS symbol.
    Set<String> vocab;
    boolean trained = false;
    float vocabSize = -1;   // V: the total vocab size including OOV
    // -1 means "not known yet."
    // Use a float to avoid integer division bugs.
    int progress;           // used by showProgress() to show progress dots

    private static final Pattern smootherRE =
        Pattern.compile("^(.*?)-?([0-9\\.]*)$");

    public static String getLMDocumentation() {
        return
            "Possible values for smoother: uniform, add1, backoff_add1, backoff_wb, loglin1\n" +
            "  (the \"1\" in add1/backoff_add1 can be replaced with any real lambda >= 0)\n" +
            "  (the \"1\" in loglin1 can be replaced with any real C >= 0)\n" +
            "lexicon is the location of the word vector file, which is only used in the loglinear model\n" +
            "trainpath is the location of the training corpus";
    }

    public static LanguageModel getLM(final String smootherL,
                                      final String lexicon) throws java.io.IOException {
        Matcher m = smootherRE.matcher(smootherL);

        if (!m.matches()) {
            System.err.format("Smoother regular expression failed for %s\n",
                              smootherL);
            System.exit(1);
        }

        final String smoother = m.group(1).toLowerCase();
        final double param;
        if (m.groupCount() >= 2 && m.group(2).length() > 0) {
            param = Double.parseDouble(m.group(2));
        } else {
            param = -1.0;
        }

        if (smoother.equals("uniform")) {
            return new UniformLanguageModel();
        } else if (smoother.equals("add")) {
            return new AddLambdaLanguageModel(param);
        } else if (smoother.equals("backoff_add")) {
            return new BackoffAddLambdaLanguageModel(param);
        } else if (smoother.equals("backoff_wb")) {
            return new BackoffWittenBellLanguageModel();
        } else if (smoother.equals("loglin")) {
            return new LoglinearLanguageModel(param, lexicon);
        } else {
            System.err.format("Unfamiliar smoother parameter: %s\n", smootherL);
            System.exit(1);
            return null;
        }
    }

    /**
     * Calculate the trigram probability p(z | x,y) in this language model.
     * This is an abstract method that must be implemented for each concrete
     * subclass of LanguageModel.
     *
     * @param x the n-2 token
     * @param y the n-1 token
     * @param z the nth token
     * @return a probability in [0,1]
     */
    public abstract double prob(final String x, final String y, final String z);

    /**
     * Read the training corpus and collect any information that might be
     * needed by prob later on.  Tokens are whitespace-delimited.
     * <p>
     * Note: In a real system, you wouldn't do this work every time you
     * ran the testing program.  You'd do it only once and save the
     * trained model to disk in some format.
     *
     * @param trainFile
     * @throws IOException
     */
    public void train(final String trainFile) throws IOException {
        System.err.format("Collecting counts from corpus %s\n", trainFile);

        if (vocab == null) {
            setVocabSize(trainFile);
        }

        // Clear out any previous training
        tokens = new HashMap<>();


        // The real work: Accumulate the type & token counts into the hash tables.

        String x = Constants.BOS;  // xy context is "beginning of sequence"
        String y = Constants.BOS;

        tokens.put(key(x, y), 1);   // count the BOS ("beginning of sequence") context
        tokens.put(y, 1);

        tokenList = new ArrayList<String>();
        tokenList.add(x);
        tokenList.add(y);
        progress = 0;
        BufferedReader reader = openCorpus(trainFile);
        String line;
        while ((line = reader.readLine()) != null) {
            for (String z : line.split("\\s+")) {   // for each token in the file
                if (!vocab.contains(z)) {
                    z = Constants.OOV;
                }
                if (this instanceof LoglinearLanguageModel
                    && ((LoglinearLanguageModel) this).vectors.containsKey(z)) {
                    z = Constants.OOL;
                    }
                count(x, y, z);       // the real work
                showProgress();     // print "....."
                x = y; y = z;           // slide trigram window forward for next word
                tokenList.add(z);
            }
        }
        reader.close();
        tokenList.add(Constants.EOS);
        System.err.println();       // done printing progress dots
        count(x, y, Constants.EOS);   // count EOS ("end of sequence") token after the final context
        // Add OOV and EOS to vocab.
        // Don't add BOS, because it is never a possible outcome but only a context.
        // Now see how big the set is.
        System.err.format("Vocabulary size is %d types including EOS and OOV\n", vocab.size());
        System.err.format("%d tokens in total\n", tokens.get(""));
        trained = true;
    }


    /**
     * When you do text categorization, call this function on the two
     * corpora in order to set the global vocabSize to the size
     * of the single common vocabulary.
     * NOTE: This function is not useful for the loglinear model, since we have
     * a given lexicon.
     */
    public void setVocabSize(String... files) {
        if (vocab != null) {
            System.err.println("Warning: vocabulary already set!");
        }

        HashMap<String, Integer> word_count = new HashMap<String, Integer>();

        // Iterate through the files.
        progress = 0;
        String line;
        for (String filename : files) {
            try {
                BufferedReader reader = openCorpus(filename);
                while ((line = reader.readLine()) != null) {
                    for (String word : line.trim().split("\\s+")) {
                        incrementMap(word, word_count);
                        showProgress();
                    }
                }
                reader.close();
            } catch (IOException e) {
                System.err.format("warning: error reading from %s\n", filename);
                e.printStackTrace(System.err);
            }
        }
        System.err.println();        // done printing progress dots

        // Add words that appear enough time to the vocabulary.
        vocab = new HashSet<>();
        for (Map.Entry<String, Integer> entry : word_count.entrySet()) {
            String word = entry.getKey();
            Integer count = entry.getValue();
            if (count >= Constants.OOV_THRESHOLD) {
                vocab.add(word);
            }
        }

        // Add OOV and EOS to vocab.
        // Don't add BOS, because it is never a possible outcome but only a context.
        vocab.add(Constants.OOV);
        vocab.add(Constants.EOS);

        // Now see how big the set is.
        vocabSize = vocab.size();
        System.err.format("Vocabulary size is %d types including OOV and EOS\n",
                          vocab.size());
    }


    // ******************* UTILITY METHODS *****************

    /**
     * Observe a token of the trigram xyz
     */
    void count(String x, String y, String z) {
        incrementMap(key(x, y, z), tokens);
        incrementMap(key(y, z), tokens);
        if (incrementMap(key(z), tokens))
            ++vocabSize;   // first time we've seen the type z
        incrementMap(key(), tokens);   // the zero-gram
    }

    /**
     * Increment count of an type in a map.  Returns whether it's being
     * incremented for the first time.
     */
    static boolean incrementMap(final String type, final Map<String, Integer> map) {
        Integer current = map.get(type);
        if (current == null) {
            map.put(type, 1);
            return true;
        } else {
            map.put(type, current + 1);
            return false;
        }
    }

    /**
     * Creates a new space-separated key from strings
     */
    static String key(String... parts) {
        StringBuffer sb = new StringBuffer();
        Iterator<String> iter = Arrays.asList(parts).iterator();
        while (iter.hasNext()) {
            sb.append(iter.next());
            if (iter.hasNext()) {
                sb.append(' ');
            }
        }
        return sb.toString();
    }

    static final BufferedReader openCorpus(String trainFile) {
        try {
            return new BufferedReader(new FileReader(new File(trainFile)));
        } catch (IOException e1) {
            try {
                return new BufferedReader(new FileReader(
                                                         new File(Constants.defaultTrainingDir + trainFile)));
            } catch (IOException e2) {
                System.err.format("Couldn't open corpus at %s or %s", trainFile,
                                  Constants.defaultTrainingDir + trainFile);
                e1.printStackTrace();
                System.exit(1);
                return null;
            }
        }
    }

    /**
     * Print a dot to stderr for every 5000 calls
     */
    final void showProgress() {
        if (progress++ % 5000 == 1) {
            System.err.print('.');
        }
    }
}

