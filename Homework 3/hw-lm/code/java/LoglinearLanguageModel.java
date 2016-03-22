/**
 * The Loglinear language model
 * This is yours to implement!
 */

import java.io.*;
import java.util.*;

class LoglinearLanguageModel extends LanguageModel {

    /**
     * The word vector for w can be found at vectors.get(w).
     * You can check if a word is contained in the lexicon using
     * if w in vectors:
     */
    Map<String, double[]> vectors;  // loaded using readVectors()

    /**
     * The dimension of word vector
     */
    int dim;

    /**
     * The constant that determines the strength of the regularizer.
     * Should ordinarily be >= 0.
     */
    double C;

    /**
     * the two weight matrices U and V used in log linear model
     * They are initialized in train() function and represented as two
     * dimensional arrays.
     */
    double[][] U, V;

    /**
     * Construct a log-linear model that is TRAINED on a particular corpus.
     *
     * @param C       The constant that determines the strength of the regularizer.
     *                Should ordinarily be >= 0.
     * @param lexicon The filename of the lexicon
     */
    public LoglinearLanguageModel(double C, String lexicon) throws java.io.IOException {
        if (C < 0) {
            System.err.println(
                    "You must include a non-negative lambda value in smoother name");
            System.exit(1);
        }
        this.C = C;
        readVectors(lexicon);
    }

    /**
     * Read word vectors from an external file.  The vectors are saved as
     * arrays in a dictionary self.vectors.
     *
     * @param filename The parameter vector: a map from feature names (strings)
     *                 to their weights.
     */
    private void readVectors(String filename) throws IOException {
        vectors = new HashMap<>();
        BufferedReader bufferedReader = new BufferedReader(new FileReader(new File(filename)));
        String header = bufferedReader.readLine();
        String[] cfg = header.split("\\s+");
        dim = Integer.parseInt(cfg[cfg.length - 1]);
        String line;
        while ((line = bufferedReader.readLine()) != null) {
            String[] arr = line.split("\\s+");
            assert arr.length == dim + 1;
            String word = arr[0];
            double[] vec = new double[dim];
            for (int i = 0; i < vec.length; ++i)
                vec[i] = Double.parseDouble(arr[i + 1]);
            vectors.put(word, vec);
        }

    }

    private void init() { // init model parameter
        this.U = new double[dim][dim];
        this.V = new double[dim][dim];
        for (int i = 0; i < dim; ++i) {
            Arrays.fill(U[i], 0.);
            Arrays.fill(V[i], 0.);
        }
    }

    /**
     * You probably want to call the parent method train(trainFile)
     * to collect n-gram counts, then optimize some objective function
     * that considers the n-gram counts, and finally call setTheta() on
     * the result of optimization.  See INSTRUCTIONS for more hints.
     */
    public void train(String trainFile) throws IOException {
        super.train(trainFile);
        if (U == null) init();
        double gamma0 = 0.1;  // initial learning rate, used to compute actual learning rate
        int epochs = 10;  // number of passes
        int N = tokenList.size() - 2;

        /**
         * Train the log-linear model using SGD.
         * ******** COMMENT *********
         * In log-linear model, you will have to do some additional computation at
         * this point.  You can enumerate over all training trigrams as following.
         * 
         * for (int i = 2; i < tokenList.size(); ++i) {
         *   String x = tokenList.get(i - 2);
         *   String y = tokenList.get(i - 1);
         *   String z = tokenList.get(i);
         * }
         *
         * Note2: You can use showProgress() to log progress.
         *
         **/

        System.err.println("Start optimizing.");
        //############################
        //TODO: Implement your SGD here
        //############################
        System.err.format("Finished training on %d tokens", tokens.get(""));
    }

    /**
     * Computes the trigram probability p(z | x,y )
     */
    public double prob(String x, String y, String z) {
        // TODO: Implement this!  Notice that you need to handle OOL words.
        System.err.println("LoglinearLanguageModel.prob() is not implemented yet");
        System.err.println("This is your job :D");
        System.exit(1);
        return 0.0;
    }

    // Feel free to add other functions as you need.
}
