package LambdaTerm;
require Exporter;
@ISA       = qw(Exporter);
@EXPORT_OK = qw(simplify simplify_safe freevars);
use bytes;

# Usage (in another Perl program):
#     use LambdaTerm qw(simplify);
#     print simplify("(%x f(x))(3)");
#
# See simplify script for a usage example for simplify_safe.
# See buildattrs script for a usage example for freevars.
#
# Note: If LambdaTerm.pm is not in the current directory when you run
# the other program, then it must be in a directory mentioned by your
# PERLLIB path environment variable.
#
# Author: Jason Eisner <jason@cs.jhu.edu>, 2001-10-18, to support 600.465 HW3.

# ----------------------------------------------------------------------

# This package provides the simplify function, which simplifies ("evaluates")
# a lambda-calculus expression represented as a string.  Some bells and
# whistles are allowed in the expressions so that you can write fairly
# natural-looking semantics.
#
#   1.  Constants and variables are alphanumeric strings (you can also use
#       the characters _ and ' in these strings).
#
#   2.  You can use commas in the natural way, as in "likes(y,x)".
#       This will be interpreted as likes(y)(x), or more precisely
#       (likes(y))(x).  (Recall that a function of two arguments must be
#       interpreted as a "curried" function of this sort because formally we
#       only have one-argument functions in the lambda calculus.)
#
#   3.  Symbol strings like ^ and -> are assumed to be infix functions,
#       so you can write "x ^ y" and not have it misinterpreted as meaning x(^,y).
#       (There is currently no way to bind definitions to these infix
#       functions though - they are just constant symbols.)
#       These infix functions have lower precedence than concatenation, 
#       so x ^ y (z) is interpreted as x ^ (y(z)), which is usually what you want.
#       (If you do intend it as a ternary operator then you should use a
#       notation like x ^ y . z  (just like "x ? y : z" in languages like C).)
#
#   4.  % represents lambda, as in "%x unicorn(x)" or "% x unicorn(x)".
#       Note that while "unicorn" denotes a particular function, the
#       "x" is a dummy variable whose name is not important, and the
#       simplifier might have to rename it to avoid conflicts with
#       other variables.
#
#   5.  You can invent other binding symbols ending in %, such as E% or
#       3% or Exists% to represent the "backwards E" of
#       existential quantification: "possible(E% x unicorn(x))".  Here
#       too x is a renameable dummy variable, rather than a constant,
#       and using the notation E% rather than just E lets the
#       simplifier know that.  (It also makes it possible to leave out
#       the parentheses in this example, for what that's worth.)
#
#   6.  You can use three kinds of parentheses if it helps you
#       read the formulas more easily: (), [], and {}.  All three kinds
#       mean the same thing.
#
#   7.  The simplifier tries to preserve as much as possible of your string's
#       original spacing and notation.  For example, the following notations
#       are equivalent but are not interconverted:
#       f(x,y), f(x)(y), f x y, (f) [ x ]  { y }
#
#   8.  The simplifier actually does more than evaluation, since it reduces
#       the entire term to a normal form.  This includes simplifying the 
#       bodies of functions that have not applied to anything.  Thus 
#       %x ((%g g(x))(h)) simplifies to %x h(x).  (But we do decline to simplify
#       further to just "h" since the user may like to show how many arguments
#       h is supposed to have and how they're expressed.)  A similar package is
#       Christophe Raffalli's "Normaliser for Pure and Typed Lambda-Calculus,"
#       available on the web.  
#
# This is the untyped lambda-calculus, so even without constants you
# can express any Turing-computable function, even though we only have
# 200 lines of code here.  The equivalence is fascinating and you
# can ask me about it if you want!  Languages that directly implement
# the untyped lambda-calculus include Scheme, LISP, ML, and in fact Perl,
# although that doesn't help us here since we can't print the internal
# representation of a Perl function.
#
# Formally there are just 3 kinds of term:
#
#    A simple constant: x, foo, -->
#    A binding term:  %x foo(x),  E%x foo(x),  %foo foo(x)
#    A juxtaposition of two subterms: foo (x), (%x foo(x)) (a)
#  	This is interpreted as applying the first subterm (the function)
#  	to the second subterm(the argument).
#
#    A sequence of more than two terms is interpreted left-associatively,
#    so f(x)(y)(z) means ((f(x))(y))(z).
#
#    You can think of , as being replaced by )( so that f(x,y,z)
#    becomes f(x)(y)(z) and for that matter (f,x,y,z) becomes
#    (f)(x)(y)(z).  All of these could be written even more simply as f x y z.
#
#    Parentheses are unnecessary except to group things, so (%x foo(x))(a)
#    could actually be written as just (%x foo x) a.
#
# How simplification works (roughly):
#    If the first term in a juxtaposition is a lambda-term, we can
#    simplify the sequence by applying it (the function) to its
#    argument.  Thus to simplify (%x foo(x))(a), we can evaluate the
#    body foo(x) with x replaced by a, yielding foo(a).
#
#    Subtle point: If the function body itself contains a dummy
#    variable a, the simplifier renames that variable to avoid
#    conflicts: (%x %a foo(x,a))(a) is treated as (%x %b foo(x,b))(a)
#    so that it simplifies not to %a foo(a,a) but rather to %b foo(a,b).
#
#    Subtle point: The simplifier often has a choice about what part of
#    the expression to simplify first.  The order doesn't matter for
#    purposes of this assignment, but for the record,
#    this simplifier uses the most general strategy, called normal-order
#    evaluation.  This is also called call-by-name or top-down or
#    leftmost outermost evaluation.  (You may also hear about lazy
#    or call-by-need evaluation, which is the same thing, only more
#    efficient.)  For more information see, e.g.,
#        http://www.csse.monash.edu.au/~lloyd/tildeFP/Lambda/Ch/01.Calc.html
#        http://wombat.doc.ic.ac.uk/foldoc/foldoc.cgi?call-by-name
#
# Implementation:
#    The implementation here is quick-and-dirty, or maybe
#    slow-and-dirty.  Everything is done in terms of strings; we
#    retokenize and reparse a subexpression every time we consider it.
#    This is obviously inefficient -- it would be faster (and probably
#    safer) to maintain a tree representation, which could include the
#    information about spacing and parentheses and such.  Even better 
#    would be to do what real languages like Scheme do, and recursively
#    evaluate while maintaining a stack of bindings.

# !!!TO DO:
#   - An exported prettyprinter for lambda terms.
#   - Add a tracing option so user can see what is going on.
#     There are some existing tracing lines commented out, but we really
#     want something that prints the entire string at every stage of
#     simplification, maybe with the hot area marked.  (Print a marker
#     line between stages, using ====---____ or ///''',,, to indicate
#     what is being reduced to what.)

# ----------------------------------------------------------------------
# DEFINITIONS OF TOKEN TYPES
# ----------------------------------------------------------------------
my($varpat)  = "[A-Za-z0-9'_]+";                  # variables are alphanumeric strings; also allow ' and _
my($oppat)   = "[^][(){}\x01\x02,%\\sA-Za-z0-9]+";  # infix operators are strings of non-alphanumerics, excepting reserved characters
my($bindpat) = "(?:%|$varpat%)";                  # binding elements look like variables plus %.  Also used to allow $oppat% (e.g., "!%") but this led to an unintuitive interpretation of (%x x).%y y since .% was parsed as a bindpat.
my($i) = 0;   # indentation level for tracing

# ----------------------------------------------------------------------
# MAIN FUNCTION
# ----------------------------------------------------------------------

# Wrappers to call from outside.

sub simplify {
  my($result) = simplify1($_[0]);   # throw away outermost parens
  return $result;
}

# A further wrapper that makes errors non-fatal.  If the input expression is
# ill-formed, we just return undef and leave the error message in $@ for
# the caller to inspect.

sub simplify_safe {
  eval { simplify($_[0]) };  # eval traps any exception that gets raised
}


# ----------------------------------------------------------------------
# MAIN FUNCTION
# ----------------------------------------------------------------------

# Just a wrapper around simp, to do tracing.

sub simplify1 {
  # print STDERR (" " x ($i+=2)),  "simplify: $_[0]\n";
  my(@resultlist) = simp($_[0]);
  # print STDERR " "x$i, "|simplified $_[0] to $resultlist[0]\n" unless $resultlist[0] eq $_[0]; i -= 2;
  return @resultlist;
}

# Simplifies a lambda expression: input and output are both strings.
#
# The output string is not surrounded by parentheses.  This means any
# initial % is conveniently exposed for further application.  But it
# also means the calling function (another instance of simp) will
# usually have to put parentheses around it before juxtaposing it with
# another term.  So we also return two other values: $prec helps the
# caller decide WHETHER to parenthesize, while @parens tells the caller
# HOW to parenthesize (via restoreparens).  $prec indicates the
# precedence of the output's top-level operator.  If that operator is
# a binder, which takes very low precedence, we return 0.  If it is an
# infix operator, we return 1.  If it is concatenation, we return 2.
# Finally, if all we have is a single term or operator, we return 3.
#
# The effect is that in an expression like f[x](y,z), the square
# brackets and the comma are a convention attached to f, and stick
# around no matter what values are substituted in for x,y,z.
# (However, if something is substituted for f and swallows up those
# arguments, their brackets disappear.)

sub simp {
  # First, split argument into a top-level sequence of expressions.
  # It would ordinarily suffice to read them in one at a time, but we
  # need to get all of them to see whether there are any infix
  # operators.
  #
  # Note that if any of the expressions starts with a parenthesis, it
  # must end with a *matching* parenthesis, or else it would have been
  # split further into two or more expressions.  So we can use
  # removeparens to remove the parentheses from the outside.

  my(@exprs) = parsetop($_[0]);   # split argument

  # Now decide what to do based on whether we have 0, 1, or more expressions
  # in our sequence.

  if (@exprs==0) {

    die "simplify: empty expression or subexpression\n";

  } elsif (@exprs==1) {

    if ($exprs[0] =~ /^\s*[[({\x01]/) {

      # The single expression is parenthesized itself, so remove the
      # parentheses and recurse to get both the simplified expression
      # and its precedence.

      my(@parens) = removeparens($exprs[0]);     # destructive
      my($result,$prec) = simplify1($exprs[0]);  # throw away inner parens
      return ($result, $prec, @parens);          # return outer parens

    } elsif ($exprs[0] =~ /^\s*$bindpat\s*$varpat\s*/o) {  # the terminal spaces \s* should actually never show up; following whitespace belongs to the wrapping of the next argument or ).

      # The expression has the form "binder variable body".
      # If the binder is %, it could be argued that we needn't
      # simplify the body, but it makes for prettier output.
      # If the binder is something else (like an existential quantifier),
      # then simplifying the body is really necessary, just as
      # if the binder were a function.

      my($binding,$body) = ($&, $');                   # binding = binder + variable; spacing = space between binding and body
      ($body,my $prec,my @parens) = simplify1($body);  # throw away $prec
      restoreparens($body, @parens, $prec >= 0);       # $prec >= 0 says we never need these parens, but if the user thought they looked pretty we'll keep them
      glue($binding,$body);
      return ($binding, 0, "", "");                    # no particular parentheses recommended for this sequence; restoreparens can make some up

    } elsif ($exprs[0] =~ /^\s*(?:$varpat|$oppat)\s*$/o) {   # the terminal spaces \s* should actually never show up; following whitespace belongs to the wrapping of the next argument or ).

      my(@parens) = removeparens($exprs[0]);  # in this case, just removes surrounding whitespace.
      return ($exprs[0], 3, @parens);         # Just an ordinary token of some sort: can't simplify it any further.

    } else {

      die "simplify: internal error: unknown form $exprs[0]]";

    }

  } elsif (grep(/^\s*$oppat\s*$/o, @exprs)) {

    # At least one of the @exprs is an unparenthesized infix operator.
    # Infix operators have lower precedence than concatenation
    # (although higher precedence than binders).  So we'll simplify
    # each concatenation of expressions between infix operators.

    my $result = ""; # simplified terms accumulate here
    my $acc = "";    # unsimplified terms accumulate here
    push(@exprs,""); # add sentinel
    while (@exprs) {
      my $expr = shift(@exprs);
      unless ($expr eq "" || $expr =~ /^\s*$oppat\s*$/o) {  # an ordinary expression
	glue($acc,$expr);
      } else {   # hitting an infix operator, or end of sequence, makes it time to reduce @acc
	if ($acc ne "") {
	  ($acc, my $prec, my @parens) = simplify1($acc);
	  restoreparens($acc, @parens,           # restore parentheses, forcing some kind of parentheses unless it has higher precedence than our current infix thing or is a final binding term (in which case binder is unambiguously a prefix operator)
			$prec > 1 || ($prec==0 && @exprs==0));
	  glue($result, $acc);
	  $acc = "";     # reset
	}
	glue($result, $expr);
      }
    }
    return ($result, 1, "", "");     # no particular parentheses recommended for this sequence; restoreparens can make some up

  } else {
    # We have an ordinary sequence of 2 or more expressions: apply the first to 
    # the rest, to the extent we can.

    # Apply $result (the result of recursively simplifying the first
    # expression) to the next expression, by substitution plus
    # recursive simplification.  Apply the result of that to the next
    # expression, and so on until we either run out of expressions
    # or we get something that we don't know how to apply (i.e., a
    # constant symbol representing a function).  

    my $result = shift(@exprs);               # result so far
    my($prec, @parens);                       # stuff returned along with that result
    $result =~ s/^\s*//; my $initspace = $&;  # save initial spacing, which is retained in an application (whereas the parens come from the body of the lambda term)
    while (1) {
      ($result,$prec,@parens) = simplify1($result);  # exposes any leading %, if this works out to a function that we can apply further
      # print STDERR " "x$i, ":result is now $result with remaining args ",join(",",@exprs),"\n";
      last unless (@exprs && $result =~ /^\s*($bindpat)\s*($varpat)\s*/o);   # can we go further?

      # $result has the form %x (or E% x) and there's something to apply it to.
      my($binder, $var, $body) = ($1,$2,$');
      die "simplify: a $binder-term is not a function and cannot be applied to an argument: $result\n"
	unless $binder eq "%";
      $result = (replace($body,$var,delparens(shift(@exprs))));  # delparens is more than cosmetic because the expression may include a final comma, which would not be legal in a substitution
      # Note that we are throwing away the parens from both applier
      # and applyee in favor of the ones from (the post-replacement
      # version of) $body.  On the next iteration, $body's parens will
      # overwrite the applier's, and notice that we explictly deleted
      # the applyee's (although it will be surrounded by () if
      # necessary).
    }
    $parens[0] = $initspace.$parens[0];

    if (@exprs==0) {    
      return ($result, $prec, @parens);   
    } else {

      # We have to now apply $result to the remaining @exprs, which we don't
      # know how to do any further, so we must return the application unevaluated.
      # We do simplify each of the remaining @exprs (though it could be
      # argued that we shouldn't: consider "runsforever((%f f f)(%f f f))"
      # vs. compare "(%x halts)((%f f f)(%f f f))").

      restoreparens($result,@parens,$prec >= 2);  # reparenthesize, forcing some kind of parentheses unless it has at least as high precedence as this concatenation (equal precedence is ok since concat is left-associative and we're first)
      while (@exprs) {
	my($expr, $prec, @parens) = simplify1(shift(@exprs));
	restoreparens($expr, @parens,           # restore parentheses exactly as in infix case (but with different precedence cutoff): force some kind of parentheses unless it has higher precedence than our current concatenation or is a final binding term (in which case binder is unambiguously a prefix operator)
		      $prec > 2 || ($prec==0 && @exprs==0));
	glue($result, $expr);
      }
      return ($result,2,"","");   # no particular parentheses recommended for this sequence; restoreparens can make some up
    }
  }
}


# ----------------------------------------------------------------------
# PARENTHESIS HANDLING
# ----------------------------------------------------------------------

# Destructively remove an outer layer of parentheses if any, along
# with the spacing outside and inside them.  Return the removed
# wrapping, which can be restored later after the inner string is
# simplified.  This function assumes that if the string starts with a
# parenthesis it ends with a *matching* parenthesis: don't give it
# "(x)(y)" since it would merrily return "x)(y"!

sub removeparens {
  my($pre,$post);
  if ($_[0] =~ s/^\s*[[({\x01]\s*//) {
    $pre = $&;
    die "simplify: internal error $pre,$_." unless $_[0] =~ s/\s*,?[])}\x02]\s*$//;
    $post = $&;
  } else {
    $_[0] =~ s/^\s*//; $pre = $&;
    $_[0] =~ s/\s*$//; $post = $&;
  }
  return ($pre,$post);
}

# Same thing, but throw away the wrapper and return the new value.

sub delparens {
  my($e) = @_;
  removeparens($e);
  $e;
}


# Destructively wrap parentheses back around an unparenthesized string.
#
# $noforce is true if the need for parentheses is merely cosmetic.  If
# not cosmetic, we have to make sure () gets added if the supplied
# parentheses are whitespace or the "as needed" parens \x01 and \x02.
# If just cosmetic, we can stick with whitespace and delete \x01 and
# \x02.

sub restoreparens {
  my($e,$pre,$post,$noforce) = @_;

  if ($noforce) {
    $pre =~ s/\x01//;
    $post =~ s/\x02//;
  } else {
    $pre =~ s/\x01/\(/;
    $post =~ s/\x02/\)/;
    $e = "($e)" if $pre =~ /^\s*$/;
  }
  $_[0] = $pre.$e.$post;
}

# ----------------------------------------------------------------------
# WORKHORSE ROUTINE: does all of the interesting work.
# ----------------------------------------------------------------------

# Remove a single expression from the beginning of $_ and write a munged
# version of it onto the end of $Eaten.  We read as little as possible,
# i.e., if $_ consists of a sequence of expressions we just read one.
#
# This function reads or modifies various variables in its caller's environment,
# which are capitalized to indicate that they have dynamic scope.
#   We modify $_ and $Eaten as just described.
#   We replace free occurrences of $Var with $Arg, which should already be
#     parenthesized.  (To turn this off, define $Var to be something like "" 
#     that won't match any variable.)
#   $Env{x} records how many instances of %x have scope over us.  This is
#     information we get from the caller: we need it to determine whether x is
#     bound or free in this expression.  We may increase it temporarily on
#     recursive calls but will change it back before we return.
#   We set $Free{x}=1 if we have encountered x free, i.e., as a constant.
#     This is information that we provide back to the caller.  Actually
#     we only do this if %Free is nonempty.
#   We rename variable x to $Newname{x}.  (Note that we only rename dummy
#     variables, not constants, whose names are fixed.)  The first time we
#     encounter x as a variable, we look at $Conflicts{x} to see whether x
#     has to be renamed, and accordingly set $Newname{x} to either x or
#     something else.  We do not rename x when it is free, i.e., a constant
#     rather than a dummy variable.
#     (Note: We could merge %Env with %Newname by having $Env{x} be a
#     stack of newnames, but we may as well use a single $Newname{x}
#     consistently to rename even occurrences of x that have nothing to
#     do with one another.)
#
# We handle a comma-separated arglist (x , y , z) by reading off
# "(x ,)" and leaving behind " (y , z)".  On the next two calls we would
# read " (y ,)" and " (z)".  When parseall reads these three
# arguments, they are glued onto the end of $Eaten using glue, which
# reconstitutes the original list perfectly.  Similarly, when simplify reads
# these three via parsetop, it will try to use them up via application, but it
# will glue simplified versions of any unused ones back together: for
# example, in (%a a)(x,y,z), simplify applies (%a a) to (x,) but doesn't
# know how to apply the resulting x to (y,) and (z), so it just
# glues them together to get x(y,z).

sub parseone {
  # print STDERR (" " x ($i+=2)),  "parseone: $_\n";
  # Note: should probably use \Q...\E construction to quote patterns.
  die "simplify: unexpected right parenthesis at end of \"$Eaten\" before \"$_\"\n" if eat("[])}\x02,]");
  die "simplify: internal error, no expressions to be found" if eat("\$");
  if (my $left = eat("[([{\x01]")) {
    my $right = $left; $right =~ tr/([{\x01/)]}\x02/;   # matching right paren char we'll look for
    &parseall;
    die "simplify: missing $right after \"$Eaten\" just before \"$_\"\n" unless eat("[$right,]");

    # If we closed with a comma, either complete it with $right  (e.g., if the 
    # expression we were given to parse was already something like "(x,)") or else 
    # pretend we saw $right and match it with a $left to start the next thing
    # (e.g., if the expression was "(x, y, z)").
    eat("\\$right") || ($Eaten .= $right, s/^\s*/$&$left/) if $Eaten =~ /,$/;

  } elsif (eat($bindpat)) {

    # We have a binder: let's get the dummy variable.
    die "simplify: expected variable following binder just before \"$_\"\n"
      unless eat("") && s/^$varpat//o;
    my($foundvar) = $&;

    # How should we rename the variable, here and any other time we
    # see it non-free?  (Our caller will also use this new name if the
    # variable appears elsewhere, since our entry in %Newname will persist
    # after we return.  This is okay, and just means that unrelated instances of
    # %x will both be renamed the same way.  We could actually avoid this by
    # making $Newname{x} be a stack (in fact, the height of the stack would
    # play the role of $Env{x}), but why bother?)

    unless (defined $Newname{$foundvar}) {   # if we haven't already chosen a renaming
      $Newname{$foundvar} = $foundvar;       # first try to rename to itself
      while ($Conflicts{$Newname{$foundvar}}) {
	# Pick a new name to try.  Here we use Perl's magic increment,
	# which should work pretty well with alphabetic variables (it turns
	# x -> y -> z -> aa -> ab ...) and not too badly with meaningful
        # variable names (e.g., subject -> subjecu -> subjecv ...)
        # An alternative would be to add ' to the current name, or to
	# maintain a number at the end of the name.
	$Newname{$foundvar}++;
      }
      # Variables that don't have newnames yet (we haven't
      # seen them before) are not allowed to conflict with the name
      # we just picked -- they might initially have had that name, or we
      # might try renaming them to that name, but either way we
      # shouldn't allow it, in case we take scope over them.
      $Conflicts{$Newname{$foundvar}} = 1;
    }
    $Eaten .= $Newname{$foundvar};

    # Ok, now that we know how to rename $foundvar when we see
    # it in the body, let's parse the body.

    $Env{$foundvar}++;   # increment number of copies of this variable with scope over us
    &parseall;           # read as much body as we possibly can
    $Env{$foundvar}--;   # pop out of that scope
    delete $Env{$foundvar} if $Env{$foundvar}==0;   # clean up after ourselves (not really necessary)

  } elsif (eat("$oppat")) {  # infix operator.
    # nothing else to do
  } elsif (eat("") && s/^$varpat//o) {   # a variable or constant
    my($foundvar)=$&;

    if ($Env{$foundvar}) {  # bound variable - we should know how to rename it

      die "simplify: internal error" unless defined $Newname{$foundvar};
      $Eaten .= $Newname{$foundvar};

    } else {                # free variable - we may have to substitute for it

      # print STDERR " " x $i, "free var: $foundvar; remaining $_\n";
      $Free{$foundvar}=1 if %Free;
      $Eaten .= ($foundvar eq $Var) ? $Arg : $foundvar;   # replace $Var by $Arg, using parens conservatively for safety; leave other variables alone

    }
  } else {
    die "simplify: internal error: don't know how to continue at \"$_\"";
  }
  # print STDERR " "x$i, "|\n"; $i-=2;
}

# Called when parseone recurses.
sub parseall {
  # print STDERR (" " x ($i+=2)),  "parseall: $_\n";
  &parseone until /^\s*($|[])}\x02,])/;   # read expressions until we hit something that would make parseone crash (end of string or right paren); compare replace, parsetop
  # print STDERR " "x$i, "|\n"; $i-=2;
}

# ----------------------------------------------------------------------
# ROUTINES THAT USE PARSING
# ----------------------------------------------------------------------

# Breaks string into a list of top-level expressions.
# Note: A top-level expression may start with spaces but does not end with them.
#
# As a side effect, if %Free is nonempty, sets $Free{v}=1 for each free
# variable v in the string.
#
# See parseone for how commas are handled.

sub parsetop {
  local($_) = @_;
  local $Var = "";   # makes sure that when we scan $_, we do no replacements
  local %Env = ();        # keep track of bound vars
  local %Conflicts = ();  # don't care about this
  local %Newname = ();    # don't care about this
  my @exprs = ();
  until (/^\s*$/) {       # read expressions till we reach end of line; compare replace, parseall
    local $Eaten = "";
    &parseone;            # get an expression
    push(@exprs,$Eaten);
  }
  return @exprs;
}

# Get list of free vars out of a lambda expression.

sub freevars {
  # print STDERR (" " x ($i+=2)),  "freevars: $_\n";
  local %Free = ("","");    # making this nonempty causes parsetop to put entries in it as a side effect (not enough to set it to (), yuck)  
  parsetop($_[0]);
  delete $Free{""};
  # print STDERR " "x$i, "|found free vars ", join(" ",keys %Free), "\n"; $i-=2;
  return keys %Free;
}

# Return a version of $_ in which free occurrences of $Var have been
# replaced by $Arg (which is passed unparenthesized by caller but is
# parenthesized between \x01 and \x02 on replacement; these special
# symbols are later deleted if possible or else replaced with ordinary
# parens).
#
# Also, variables in $_ are renamed as necessary to avoid capturing
# the free variables of $Arg.  (The new names must also avoid
# capturing free variables of either $f or $Arg -- i.e., (%x %e
# f(x,e)) (e(g)) must rename e, but mustn't rename it to f or g!  --
# and they must not conflict with one another, either.)
#
# The renaming is aggressive - if foo appears free in $Arg or $_, we
# rename all its non-free instances in $_, even ones that don't
# take scope over $Var (including any non-free instances of $Var itself!).
# In other words, we may do some unnecessary renaming.

sub replace {
  local($_,$Var,$Arg) = @_;   # $Var tells parse what to replace
  # print STDERR (" " x ($i+=2)),  "replace $Var with $Arg in $_\n";
  $Arg =~ s/^\s*//;           # kill initial whitespace in replacement.  (Should have no final whitespace.)
  $Arg = "\x01$Arg\x02";        # protect with temporary parentheses
  # Figure out which variables we must rename.
  local %Conflicts;           # records variables that are free in arg
  {
    local %Free = ("","");    # making this nonempty causes parsetop to put entries in it as a side effect (not enough to set it to (), yuck)
    parsetop($Arg);           # throw away result, but figure out which vars are free
    parsetop($_);             # and which vars are free in $_ as well
    %Conflicts = (%Free);
  }

  # Okay, go ahead and process $_.
  local %Newname = ();        # renaming table to avoid conflicts
  local %Env = ();            # keep track of bound variables
  local $Eaten = "";
  &parseone until eat("\$"); # read expressions till we reach end of $_; compare parsetop, parseall
  # print STDERR " "x$i, "|replaced to $Eaten\n"; $i-=2;
  return $Eaten;
}

# ----------------------------------------------------------------------
# LOW-LEVEL ROUTINES FOR SCANNING INPUT
# ----------------------------------------------------------------------

# If $pattern matches at beginning of $_ (perhaps with preceding
# whitespace), remove it from $_ and glue it to end of $Eaten.
# Return whether we got such a match.  (Actually return the match
# string itself (without whitespace) for the caller's inspection,
# unless it has a false value.)
#
# Note that eat("") eats leading whitespace from $_.
sub eat {
  my($pattern)=@_;
  if (s/^\s*($pattern)//) {
    my($match) = $1;
    glue($Eaten, $&);
    return $match ? $match : 1;
  } else {
    return "";
  }
}

# Concatenate $y onto $x (destructively), fixing up commas (see parseone for
# details) and spaces.
sub glue {
  my($x, $y) = @_;

  # If $x ends in comma followed by close paren, delete the close paren and
  # also the open paren that must start $y.
  $y =~ s/^(\s*)[[({\x01]/$1/ || die "simplify: internal error" if $x =~ s/,[])}\x02]$/,/;

  # Insert whitespace if $x and $y are in danger of glomming tokens together.
  # I'm not sure whether this ever happens in practice.
  $x .= " ", warn "added space to combine $x and $y." if $x =~ /$varpat$/o && $y =~ /^$varpat/o || $x =~ /$oppat$/o && $y =~ /^$oppat/o;

  $_[0] = $x.$y;
}


1;    # signal that this module was loaded successfully
