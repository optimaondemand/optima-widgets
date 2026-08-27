# -*- coding: utf-8 -*-
"""clt_author_bank.py -- the Classic Learning Test Author Bank, verbatim.

Source:    https://www.cltexam.com/tests/authors/
Retrieved: 2026-08-27
Authority: CLT publishes this list itself. Two-thirds of CLT and CLT10 reading
           and writing passages are drawn from these authors.

IMPORTANT -- this is an AUTHOR list, not a title list. CLT does not publish
"the CLT reading list" of specific books. So a title in the Optima catalogue is
CLT-relevant when ITS AUTHOR is in this bank; the bank never says which of that
author's works appear. Seven entries are anonymous works rather than authors and
are matched on title instead; they are marked WORKS below.

Do not add an author here because it feels canonical. This file is a copy of a
published list, and its value is that it is exactly that.
"""

# Anonymous or collectively-authored works. Matched against a title, not an author.
WORKS = [
    "The Epic of Gilgamesh",
    "Beowulf",
    "The Thousand and One Nights",
    "The Nibelungenlied",
    "Magna Carta",
    "The Saga of Erik the Red",
    "Pearl",
]

AUTHORS = [
    "Homer", "Hesiod", "Aesop", "Confucius", "Aeschylus", "Sophocles",
    "Herodotus", "Euripides", "Thucydides", "Hippocrates", "Plato", "Aristotle",
    "Euclid", "Archimedes", "Terence", "Cicero", "Julius Caesar", "Lucretius",
    "Virgil", "Livy", "Ovid", "Seneca the Younger", "Josephus", "Plutarch",
    "Epictetus", "Tacitus", "Tertullian", "Origen", "Athanasius",
    "Gregory of Nyssa", "Jerome", "Augustine of Hippo", "Boethius", "Benedict",
    "Procopius", "Gregory the Great", "Bede the Venerable", "Avicenna",
    "Anselm of Canterbury", "Peter Abelard", "Bernard of Clairvaux",
    "Hugh of St. Victor", "Hildegard of Bingen", "Heloise d'Argenteuil",
    "Averroes", "Moses Maimonides", "Marie de France", "Thomas Aquinas",
    "Dante Alighieri", "Giovanni Boccaccio", "John Wycliffe", "Geoffrey Chaucer",
    "Julian of Norwich", "Catherine of Siena", "Christine de Pizan",
    "Thomas a Kempis", "Thomas Malory", "Desiderius Erasmus",
    "Niccolo Machiavelli", "Nicolaus Copernicus", "Thomas More", "Martin Luther",
    "Bartolome de Las Casas", "John Calvin", "Teresa of Avila",
    "Michel de Montaigne", "Francis Bacon", "William Shakespeare",
    "Galileo Galilei", "John Donne", "Thomas Hobbes", "Rene Descartes",
    "John Milton", "Blaise Pascal", "Margaret Cavendish", "Robert Boyle",
    "John Bunyan", "John Locke", "Isaac Newton", "Gottfried Leibniz",
    "Charles Montesquieu", "Voltaire", "Jonathan Edwards", "Benjamin Franklin",
    "David Hume", "Jean-Jacques Rousseau", "Adam Smith", "Immanuel Kant",
    "Edward Gibbon", "Antoine Lavoisier", "Thomas Jefferson", "Olaudah Equiano",
    "Johann Wolfgang von Goethe", "James Madison", "Mary Wollstonecraft",
    "Georg W. F. Hegel", "Jane Austen", "Jakob & Wilhelm Grimm", "Mary Shelley",
    "Sojourner Truth", "John Henry Newman", "Alexis de Tocqueville",
    "Hans Christian Andersen", "John Stuart Mill", "Edgar Allan Poe",
    "Charles Darwin", "Charles Dickens", "Soren Kierkegaard", "Charlotte Bronte",
    "Henry David Thoreau", "Karl Marx", "Frederick Douglass", "George Eliot",
    "Herman Melville", "Susan B. Anthony", "Fyodor Dostoevsky", "Gregor Mendel",
    "Louis Pasteur", "Leo Tolstoy", "Mark Twain", "Friedrich Nietzsche",
    "Oscar Wilde", "Sigmund Freud", "Anna Julia Cooper", "Anton Chekhov",
    "Alfred North Whitehead", "Ida B. Wells", "W. E. B. Du Bois",
    "Mahatma Gandhi", "Willa Cather", "G. K. Chesterton", "Albert Einstein",
    "Virginia Woolf", "John Maynard Keynes", "Franz Kafka",
    "Ludwig Wittgenstein", "Zora Neale Hurston", "J. R. R. Tolkien",
    "Dorothy Sayers", "F. Scott Fitzgerald", "C. S. Lewis", "Ernest Hemingway",
    "Jorge Luis Borges", "Friedrich Hayek", "Langston Hughes", "John Steinbeck",
    "George Orwell", "Hannah Arendt", "Albert Camus", "Aleksandr Solzhenitsyn",
    "James Baldwin", "Flannery O'Connor", "Elie Wiesel",
    "Martin Luther King Jr.", "Toni Morrison",
]

# Surnames that are the practical match key, where the bank's form and a book
# list's form differ. Kept explicit rather than inferred, so a wrong match is
# visible in a diff rather than buried in a heuristic.
SURNAME_HINTS = {
    "jakob & wilhelm grimm": ["grimm"],
    "julius caesar": ["caesar"],
    "hugh of st. victor": ["hugh"],
    "martin luther king jr.": ["king"],
    "w. e. b. du bois": ["du bois", "dubois"],
    "g. k. chesterton": ["chesterton"],
    "j. r. r. tolkien": ["tolkien"],
    "c. s. lewis": ["lewis"],
    "f. scott fitzgerald": ["fitzgerald"],
    "susan b. anthony": ["anthony"],
    "ida b. wells": ["wells"],
    "georg w. f. hegel": ["hegel"],
    "alfred north whitehead": ["whitehead"],
    "seneca the younger": ["seneca"],
    "bede the venerable": ["bede"],
    "gregory the great": ["gregory"],
    "thomas a kempis": ["kempis"],
}
