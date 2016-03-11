/** 
 * The add-lambda language model. The trigram probability p(z | xy) assigned by 
 * this model is a generalization of the MLE estimate c(xyz)/c(xy). Namely, 
 * (c(xyz) + lambda) / (c(xy) + lambda * V)
 * for a given parameter lambda. 
 */
class AddLambdaLanguageModel extends LanguageModel {
  final double lambda;

  public AddLambdaLanguageModel(double lambda) throws java.io.IOException {
    if (lambda < 0) {
      System.err.println(
          "You must include a non-negative lambda value in smoother name");
      System.exit(1);
    }
    this.lambda = lambda;
  }
  
  /**
   * Computes an estimate of the trigram probability p(z | x,y)
   * according to the add-lambda language model.
   * @param x the n-2 token
   * @param y the n-1 token
   * @param z the nth token
   * @return a probability in [0,1]
   */
  public double prob(final String x_, final String y_, final String z_) {
    // Replace out-of-vocabulary words with OOV symbol.
    String x = vocab.contains(x_) ? x_ : Constants.OOV;
    String y = vocab.contains(y_) ? y_ : Constants.OOV;
    String z = vocab.contains(z_) ? z_ : Constants.OOV;

    final String xyz = x + " " + y + " " + z;
    final String xy = x + " "  + y;
    
    final double xyzCount;
    Integer xyzCountInt = tokens.get(xyz);
    if (xyzCountInt == null) {
      xyzCount = 0.0;
    } else {
      xyzCount = (double) xyzCountInt;
    }
    
    final double xyCount;
    Integer xyCountInt = tokens.get(xy);
    if (xyCountInt == null) {
      xyCount = 0.0;
    } else {
      xyCount = (double) xyCountInt;
    }
    
    return (xyzCount + lambda) / (xyCount + lambda * vocabSize);
  }  
}
