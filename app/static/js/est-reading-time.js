/* Count words in article & calculate estimate read time. */
const article = document.getElementsByClassName('article-item')

// Iterate through the elements text content.  Remove white space from both sides of a string
// and split on any sequence of white spaces, including tabs, newlines etc.. using regex.

let wordCount = 0
for (let i = 0; i < article.length; i++) { wordCount += article[i].textContent.trim().split(/\s+/).length }

// Calculate estimate reading time and round to nearest minute.
estReadTime = Math.round(wordCount / 200)

if (estReadTime < 1) { estReadTime = 1 }

// insert word count.
document.getElementsByClassName('word-count')[0].textContent = estReadTime + " minute read."