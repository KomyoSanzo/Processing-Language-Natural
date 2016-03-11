/** 
 * The uniform language model: all words (including OOV) are equally likely.
 * The probability p(z | xy) assigned by this model is simply the uniform 
 * distribution 1/V for the vocabulary size V.
 */
class UniformLanguageModel extends LanguageModel {

  /** 
   * Constructs a uniform language model.  Even though it's just a 
   * uniform distribution, it needs to train on a corpus in order to 
   * find the vocabulary size. 
   */
  public UniformLanguageModel() throws java.io.IOException {
  }

  /**
   * Computes the trigram probability p(z | x,y)
   * according to the uniform language model.
   *
   * @param x the token before the previous token
   * @param y the previous token
   * @param z the current token
   * @return a probability in [0,1]
   */
  public double prob(final String x, final String y, final String z) {
    return 1.0 / vocabSize;
  }  
}
