import java.io.*;
import java.util.*;

/**
 * The backoff Witten-Bell language model.
 * This is yours to implement!  (for extra credit)
 * @author YOUREMAIL (YOURNAME)
 */
class BackoffWittenBellLanguageModel extends LanguageModel {
  
  /** Some additional data needed for Witten-Bell. */
  private Map<String,Integer> typesAfter;  // the T(...) function; needed by prob()
  private List<String> bigrams;            // list of all bigrams; built and used during train()
  private List<String> trigrams;           // list of all trigrams; built and used during train()


  /** 
   * Constructs a Witten-Bell backoff language model trained on the given file.
   */
  public BackoffWittenBellLanguageModel() throws java.io.IOException {
  }


  /**
   * Computes the trigram probability p(z | x,y )
   * This is yours to implement!
   */
  public double prob(String x, String y, String z) {
    System.err.println("BackoffWittenBellLanguageModel.prob() is not implemented yet");
    System.err.println("This is your job :D");
    System.exit(1);
    return 0.0;
  }

  @Override
  public void train(final String trainFile) throws IOException {

    // Initialize the extra data structures we need for Witten-Bell.
    typesAfter = new HashMap<String, Integer>();
    bigrams = new ArrayList<String>();
    trigrams = new ArrayList<String>();

    // Call the general training method for counting unigrams,
    // bigrams, and trigrams.  Because it calls count(), our
    // overriding of count() arranges for it to also populate
    // those extra data structures.
    super.train(trainFile);

    /* ******** COMMENT *********
     * You will now have to do some additional computation.  The
     * following code illustrates how you can iterate over all
     * observed bigram types.  (It just prints them.)
     *
     * for (String bigramStr : bigrams) {
     *   String[] b = bigramStr.split(" ");
     *   String word1 = b[0];
     *   String word2 = b[1];
     *   System.out.format("%s %s\n", bigram1, bigram2);
     * }
     *
     * **************************/
  }

  /** Does same thing as super.count(), but also some extra 
   * Witten-Bell-specific work.
   */
  @Override
  void count(String x, String y, String z) {
    if (incrementMap(key(x,y,z), tokens)) { // incrementMap returns true if first time we've seen this n-gram
      trigrams.add(key(x,y,z));  
      incrementMap(key(x,y), typesAfter);
    }
    if (incrementMap(key(y,z), tokens)) {
      bigrams.add(key(y,z));
      incrementMap(key(y), typesAfter);
    }
    if (incrementMap(key(z), tokens)) {
      ++vocabSize;   
      incrementMap(key(), typesAfter);
    }
    incrementMap(key(), tokens);   // the zero-gram
  }
    
}