filter('all');
function filter(c) {
    var x, i;
    x = document.getElementsByClassName("hang11");
    if (c == "all") c = "";
    for (i = 0; i < x.length; i++) {
        removeClass(x[i], "show");
        if (x[i].className.indexOf(c) > -1) addClass(x[i], "show");
    }
}

function addClass(element, name) {
    var arr1, arr2;
    arr1 = element.className.split(" ");
    arr2 = name.split(" ");
    for (var i = 0; i < arr2.length; i++) {
        if (arr1.indexOf(arr2[i]) == -1) {
            element.className += " " + arr2[i];
        }
    }
}

function removeClass(element, name) {
    var arr1, arr2;
    arr1 = element.className.split(" ");
    arr2 = name.split(" ");
    for (var i = 0; i < arr2.length; i++) {
        while (arr1.indexOf(arr2[i]) > -1) {
            arr1.splice(arr1.indexOf(arr2[i]), 1);
        }
    }
    element.className = arr1.join(" ");
}
function showImage(id, src) {
    var largeImage = document.getElementById(id);
    largeImage.src = src;
}

function resetImage(id) {
    var largeImage = document.getElementById(id);
    var defaultSrc = largeImage.getAttribute('data-default-src');
    largeImage.src = defaultSrc;
}
document.addEventListener('DOMContentLoaded', () => {
    function showImage(id, src) {
        document.getElementById(id).src = src;
    }

    function resetImage(id) {
        var image = document.getElementById(id);
        image.src = image.getAttribute('data-default-src');
    }
    window.searchProducts = function() {
        var input = document.getElementById('search-input').value.toLowerCase();
        var products = document.querySelectorAll('.hang11');
        
        products.forEach(product => {
            var title = product.querySelector('h3').innerText.toLowerCase();
            if (title.includes(input)) {
                product.style.display = 'block';
            } else {
                product.style.display = 'none';
            }
        });
        
        return false;
    }
});

