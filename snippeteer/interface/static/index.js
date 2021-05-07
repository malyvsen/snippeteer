// Show / hide results
const codeElements = document.getElementsByClassName('code-element');
const idToElement = {};
for (let codeElement of codeElements) {
    idToElement[codeElement.getAttribute('data-id')] = codeElement;
    codeElement.style.display = 'none';
}

function toggleElement(id) {
    if (isElementShown(id)) {
        idToElement[id].parentElement.firstElementChild.classList.remove('bg-gray-700')
    } else {
        idToElement[id].parentElement.firstElementChild.classList.add('bg-gray-700')
    }
    idToElement[id].style.display = isElementShown(id) ? 'none' : 'block';
}

function isElementShown(id) {
    return idToElement[id].style.display !== 'none';
}

// Search
document.getElementById('query').addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
        search();
    }
})

function search() {
    const freeTextQuery = document.getElementById('query').value;
    const queryFilters = filters.map(filter => {
        return `${filter.exclude ? '!' : ''}${filter.key}:${filter.exact ? '=' : ''}${filter.value}`;
    }).join(' ');
    const value = encodeURIComponent((freeTextQuery + ' ' + queryFilters).trim());
    const searchParams = new URLSearchParams(location.search);
    searchParams.set('q', value);
    searchParams.set('p', '1');
    location.search = searchParams.toString();
}

// Add / remove filters
let filters = [];
const filterElements = document.getElementsByClassName('search-filter');
for (let filterElement of filterElements) {
    filters.push({
        key: filterElement.getAttribute('data-key'),
        value: filterElement.getAttribute('data-value'),
        exclude: filterElement.getAttribute('data-exclude') === 'True',
        exact: filterElement.getAttribute('data-exact') === 'True'
    });
}

function removeFilter(id) {
    filters.splice(id, 1);
    search();
}

function addFilter(key, value, exclude, exact) {
    filters = filters.filter(filter => filter.key !== key || filter.value !== value);
    filters.push({key, value, exclude, exact});
    search();
}

// Apply star / ops filters
function applyRangeFilters() {
    const minStars = document.getElementById('minStars').value;
    const maxOps = document.getElementById('maxOps').value;
    const searchParams = new URLSearchParams(location.search);
    searchParams.set('s', minStars);
    searchParams.set('o', maxOps);
    searchParams.set('p', '1');
    location.search = searchParams.toString();
}