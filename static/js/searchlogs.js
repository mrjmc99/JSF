document.querySelector('form').addEventListener('submit', function() {
    document.querySelector('input[type="submit"]').disabled = true;
    document.querySelector('#progressMessage').style.display = 'block';
});
