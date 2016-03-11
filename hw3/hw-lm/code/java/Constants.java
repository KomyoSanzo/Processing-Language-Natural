class Constants {
    public static final String courseDir = "/usr/local/data/cs465/";
    public static final String defaultTrainingDir =
            "/usr/local/data/cs465/hw-lm/All_Training/";
    public static final String BOS = "BOS";   // special word type for context at Beginning Of Sequence
    public static final String EOS = "EOS";   // special word type for observed token at End Of Sequence
    public static final String OOV = "OOV";   // special word type for all Out-Of-Vocabulary words
    public static final String OOL = "OOL";   // special word type for all Out-Of-Lexicon words
    public static final double LOG2 = Math.log(2);
    // Note: You should only convert to log base 2 when printing out cross-entropy.
    // Everywhere else, the log-probabilities you work with should be natural logs,
    // for simplicity and speed.
    public static final int OOV_THRESHOLD = 3;   // minimum number of occurrence for a word to be considered in-vocabulary.
}
