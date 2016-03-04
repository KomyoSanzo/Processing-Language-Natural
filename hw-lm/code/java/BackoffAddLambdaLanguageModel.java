/**
 * The backoff add-lambda language model
 * This is yours to implement!
 * @author YOUREMAIL (YOURNAME)
 */
class BackoffAddLambdaLanguageModel extends LanguageModel {
  final double lambda;

  /** 
   * Constructs an add-lambda language model trained on the given file.
   */
  
  public BackoffAddLambdaLanguageModel(double lambda) throws java.io.IOException {
    if (lambda < 0) {
      System.err.println(
          "You must include a non-negative lambda value in smoother name");
      System.exit(1);
    }
    this.lambda = lambda;
  }
  
  /**
   * Computes the trigram probability p(z | x,y )
   * This is yours to implement!
   */
  public double prob(String x, String y, String z) {
    System.err.println("BackoffAddLambdaLanguageModel.prob() is not implemented yet");
    System.err.println("This is your job :D");
    System.exit(1);
    return 0.0;
  }
}
