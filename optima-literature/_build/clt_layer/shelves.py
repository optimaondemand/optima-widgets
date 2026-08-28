# -*- coding: utf-8 -*-
"""Shelf per CLT addition, using the existing 11-shelf taxonomy only.

genre_for() falls back to "Unclassified" for anything the student library does
not carry, and it carries almost none of these. Rather than ship 129
Unclassified cards, each is shelved here by hand -- the same posture as
genres.CURATED, which exists for exactly this reason.
"""
BY_SHELF = {
    "Philosophy, Politics & Theology": [
        "Cicero", "Lucretius", "Seneca the Younger", "Epictetus",
        "Tertullian", "Origen", "Athanasius", "Gregory of Nyssa", "Jerome",
        "Augustine of Hippo", "Boethius", "Benedict", "Gregory the Great",
        "Anselm of Canterbury", "Bernard of Clairvaux", "Hugh of St. Victor",
        "Hildegard of Bingen", "Averroes", "Moses Maimonides",
        "Thomas Aquinas", "John Wycliffe", "Julian of Norwich",
        "Catherine of Siena", "Christine de Pizan", "Thomas a Kempis",
        "Desiderius Erasmus", "Niccolo Machiavelli", "Thomas More",
        "Martin Luther", "John Calvin",
        "Teresa of Avila", "Michel de Montaigne", "Francis Bacon",
        "Thomas Hobbes", "Rene Descartes", "Blaise Pascal", "John Locke",
        "Gottfried Leibniz", "Charles Montesquieu", "Jonathan Edwards",
        "David Hume", "Jean-Jacques Rousseau", "Adam Smith", "Immanuel Kant",
        "Georg W. F. Hegel", "Mary Wollstonecraft", "Alexis de Tocqueville",
        "John Stuart Mill", "Soren Kierkegaard", "Henry David Thoreau",
        "Karl Marx", "Ludwig Wittgenstein", "G. K. Chesterton",
        "Friedrich Hayek", "Hannah Arendt", "Martin Luther King Jr.",
        "John Henry Newman",
    ],
    "Nonfiction & Biography": [
        "Herodotus", "Thucydides", "Hippocrates", "Euclid", "Archimedes",
        "Julius Caesar", "Livy", "Josephus", "Plutarch", "Tacitus",
        "Procopius", "Bede the Venerable", "Avicenna", "Peter Abelard",
        "Heloise d'Argenteuil", "Nicolaus Copernicus", "Galileo Galilei",
        "Isaac Newton", "Robert Boyle", "Antoine Lavoisier",
        "Edward Gibbon", "Benjamin Franklin", "Olaudah Equiano",
        "Sojourner Truth", "Susan B. Anthony", "Charles Darwin",
        "Gregor Mendel", "Louis Pasteur", "Sigmund Freud",
        "Anna Julia Cooper", "Alfred North Whitehead", "Ida B. Wells",
        "W. E. B. Du Bois", "Mahatma Gandhi", "Albert Einstein",
        "John Maynard Keynes", "James Baldwin",
    ],
    "Drama & Poetry": [
        "Hesiod", "Aeschylus", "Euripides", "Terence", "Ovid", "John Donne",
        "John Milton", "Edgar Allan Poe", "Oscar Wilde", "Anton Chekhov",
        "Johann Wolfgang von Goethe", "Marie de France", "Pearl",
    ],
    "Myth, Legend & Folklore": [
        "The Epic of Gilgamesh", "The Nibelungenlied",
        "The Saga of Erik the Red", "Thomas Malory",
        "Jakob & Wilhelm Grimm",
    ],
    "Classics": [
        "Giovanni Boccaccio", "John Bunyan",
    ],
    "Novels & Literary Fiction": [
        "Voltaire", "George Eliot", "Herman Melville", "Leo Tolstoy",
        "Willa Cather", "Ernest Hemingway", "Jorge Luis Borges",
        "Albert Camus", "Aleksandr Solzhenitsyn", "Toni Morrison",
    ],
    "Mystery, Adventure & Humor": ["Dorothy Sayers"],
    "Fantasy & Science Fiction": ["Margaret Cavendish"],
    "American Founding & Documents": ["Thomas Jefferson", "Magna Carta"],
}

SHELF = {bank: shelf for shelf, banks in BY_SHELF.items() for bank in banks}
