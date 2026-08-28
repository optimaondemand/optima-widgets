# -*- coding: utf-8 -*-
"""clt_titles.py -- which Optima titles sit in the CLT Author Bank.

FROZEN ON PURPOSE. Derived once from clt_author_bank.py by matching author
names, then reviewed by hand; kept as an explicit list rather than recomputed,
for the same reason course_editions.py is an explicit dict: a fuzzy match that
silently changes between builds is worse than a list somebody can read.

The bank is an AUTHOR list. CLT does not publish which of an author's works
appear on the exam, so this tag means "by an author CLT draws from", never
"this exact book is on a CLT reading list".

Rulings recorded when this was built (2026-08-27):
  INCLUDED  Aesop's Fables (K, 1) -- AEsop is a bank entry; the Optima entry is
            a retelling, so the author field holds the reteller, not the author.
  INCLUDED  The Arabian Nights (6) -- "The Thousand and One Nights" is a bank entry.
  EXCLUDED  King Arthur / The Adventures of Robin Hood (6), both Roger Lancelyn
            Green. Neither is in the bank. Malory is, for Le Morte d'Arthur;
            these are not Malory.
  EXCLUDED  The Twenty-One Balloons (3) -- William Pene du Bois, a different
            person from W. E. B. Du Bois.
  EXCLUDED  The Waste Land (12) -- T. S. Eliot, a different person from George
            Eliot.

Keys are (grade, title) exactly as the catalogue holds them. A title that is
renamed upstream stops matching, which shows up as a lost badge rather than a
wrong one -- the failure that is easiest to notice.
"""

# (grade, title) -> the bank entry that put it here
CLT = {
    ('K', "Aesop's Fables ( The Lion's Share)The Ant and the Grasshopper, The Town Mouse and the Country Mouse, The Fox and the Crow)"):
        'AEsop (retold)',
    ('K', 'The Ugly Duckling'):
        'Hans Christian Andersen',
    ('1', "Aesop's Fables"):
        'AEsop (retold)',
    ('3', 'The Chronicles of Narnia: The Lion, The Witch, and the Wardrobe'):
        'C. S. Lewis',
    ('4', 'The Adventures of Tom Sawyer'):
        'Mark Twain',
    ('4', 'The Chronicles of Narnia: Prince Caspian'):
        'C. S. Lewis',
    ('5', 'Dreams'):
        'Langston Hughes',
    ('6', 'The Arabian Nights'):
        'The Thousand and One Nights (retold)',
    ('7', 'A Christmas Carol'):
        'Charles Dickens',
    ('8', 'Emma'):
        'Jane Austen',
    ('8', 'Out of the Silent Planet'):
        'C. S. Lewis',
    ('8', 'Romeo and Juliet'):
        'William Shakespeare',
    ('9', 'Beowulf'):
        'Beowulf',
    ('9', 'Electra'):
        'Sophocles',
    ('9', 'The Canterbury Tales'):
        'Geoffrey Chaucer',
    ('9', 'The Divine Comedy'):
        'Dante Alighieri',
    ('9', 'The Taming of the Shrew'):
        'William Shakespeare',
    ('10', "A Midsummer Night's Dream"):
        'William Shakespeare',
    ('10', 'Animal Farm'):
        'George Orwell',
    ('10', 'Julius Caesar'):
        'William Shakespeare',
    ('10', 'Macbeth'):
        'William Shakespeare',
    ('10', 'Night'):
        'Elie Wiesel',
    ('10', 'Oedipus the King, Oedipus at Colonus, Antigone'):
        'Sophocles',
    ('10', 'The Great Gatsby'):
        'F. Scott Fitzgerald',
    ('10', 'The Odyssey'):
        'Homer',
    ('10', 'Their Eyes Were Watching God'):
        'Zora Neale Hurston',
    ('11', 'Great Expectations'):
        'Charles Dickens',
    ('11', 'Hamlet'):
        'William Shakespeare',
    ('11', 'Jane Eyre'):
        'Charlotte Bronte',
    ('11', 'Narrative of the Life of Frederick Douglass'):
        'Frederick Douglass',
    ('11', 'The Adventures of Huckleberry Finn'):
        'Mark Twain',
    ('11', 'The Grapes of Wrath'):
        'John Steinbeck',
    ('12', '1984'):
        'George Orwell',
    ('12', "A Room of One's Own"):
        'Virginia Woolf',
    ('12', 'Frankenstein'):
        'Mary Shelley',
    ('12', 'Nicomachean Ethics'):
        'Aristotle',
    ('12', 'Poetry'):
        'Langston Hughes',
    ('12', 'Republic- Allegory of the Cave'):
        'Plato',
    ('12', 'The Aeneid'):
        'Virgil',
    ('12', 'The Brothers Karamazov'):
        'Fyodor Dostoevsky',
    ('12', 'The Fellowship of the Ring'):
        'J. R. R. Tolkien',
    ('12', 'The Metamorphosis'):
        'Franz Kafka',
    ('12', 'Wise Blood'):
        "Flannery O'Connor",

    # --- added 2026-08-28 with the CLT Author Bank layer.
    # Author matching could not see these three: all three catalogue records
    # carry an EMPTY author field, so there was no surname to match the bank
    # against. Found by listing the author-less records rather than by matching.
    # They are badged here, NOT duplicated into clt_additions.py.
    ('12', 'Confucian Analects'):
        'Confucius',
    ('12', "Excerpts from Nietzsche's writings"):
        'Friedrich Nietzsche',
    # source_corrections.py rewrites "The Federalist's Papers" before anything
    # derives from the title, so the key here is the corrected form.
    ('11', 'The Federalist Papers'):
        'James Madison',
}


def is_clt(grade, title):
    return (grade, title) in CLT


def bank_entry(grade, title):
    return CLT.get((grade, title))
