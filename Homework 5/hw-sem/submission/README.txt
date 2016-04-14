Question 3
a) 
i. %x loves (Mary, x) (John)
ii. loves (Mary, John)

b) %y loves(Mary, y); V NP

c) 
i. %y A%x woman(x) => loves(x, y)
ii. f is "loves every woman" (or for all X, if x is a woman then y loves x)
	f(John) is "Johns loves every woman" (or for all X, if x is a woman then Johns loves x)
	
d) f = %y %x Obviously(y(x)). To construct "Sue obviously loves Mary", let y = (%x loves(Mary, x))(Sue). 

e) f = %x(%y(%z act(z, loving), lovee(z, x), lover(z, y)))

f) g = %f%y%z f(y)(z), manner(z, passionate)

g) 
i. f = %x A%y woman(y) => x(y)
ii. Every woman loves Mary.
	Loves Mary.
	Every woman.

h) 
i. g = %f %x A%y f(y) => x(y)
ii. "Every"

i)
i. %y y(Papa)
ii. This maintains consistency in its way of use. This allows us to not have to worry about having separate rules such as NP => Det Noun.

Question 4

''Laura say -s that George might sleep on the floor ! ''
Breaks on the preposition; on the floor is not assigned to sleep, but instead to Laura says. This can likely be fixed with a different parse.

''Papa would have eat -ed his sandwich -s . ''
It is ambiguous as to who owns the sandwich. Sandwich is assigned to `his'. This is technically okay but I'm including this to demonstrate how the ambiguity of the original sentence affects the attributes/semantics.

''Papa sleep -s every bon bon with a spoon . ''
It breaks at ``sleeps every bon bon''. Sentence is grammatical and parses correctly, but gives the error: '' No consistent way to assign attributes!''. This may be possibly fixed with a different parse, but using the original meaning of the sentence this is correct. Sleeps cannot have "every bonbon" as an object.

''A bon bon on the spoon entice -0 . '
No consistent way to assign attributes! error. This makes sense as there is a tense error in entice.


''the fine and blue woman and every man must have eat -ed two sandwich -s and sleep -ed on the floor .'''
No consistent way to assign attributes!; This is likely due to our parse as the VP cannot have attributes assigned correctly. This could likely be fixed with a different parse.
Question 5
See the Q5english.gra file. 
Three sentences were tested: 
Johnny ate the caviar.
Johnny ate caviar.
and All caviar is expensive. 

The grammar worked well with all of them except "Johnny ate caviar." This is likely due to the fact that there is no rule in the grammar file that states a verb can follow a mass noun. 


Question 6
i.
"Two": We are essentially making sure that the two things are not equal using domain restriction. The predicate is then applied to both things.
"The" singular: There exists an object that satisfies te domain restriction and that the predicate is correct for this one subject.
"The" plural: There exists a set of subjects such that everything within the set satisfies the domain restriction and all is correct for the predicate.

ii. 2(1)(3)