// This section of code is for obtaining the CSRF token which is needed for the AJAX request used later in the code
// This code is taken from Django's CSRF documentation
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

// Function to hide the edit button for the post in question, and display the edit text box and save button
function makeEditable(post_id) {
    let form_id = `${post_id}_edit_form`;
    let button_id = `${post_id}_edit_button`;
    let original_id = `${post_id}_post_body`;
    document.getElementById(form_id).style.display = 'block';
    document.getElementById(button_id).style.display = 'none';
    document.getElementById(original_id).style.display = 'none';
}

// Function to save changes made to the post in question
function saveEdit(post_id) {
    // Set variables up for every part of this post we will manipulate
    let form_id = `${post_id}_edit_form`;
    let button_id = `${post_id}_edit_button`;
    let original_id = `${post_id}_post_body`;
    let body_id = `${post_id}_edit_content`;
    
    // Get the edited text into the edited_content variable
    edited_content = document.getElementById(body_id).value;

    // Use the fetch API to update the server with the edited post, then change our HTML to display the change
    // Use the path to the edit url (functionality written in views.py)
    fetch('/edit/' + post_id, {
        method: 'PUT', // PUT method for updating existing data
        headers: { // Set the X-CSRFToken header to the csrf token obtained from getCookie
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({
            content: edited_content,
        })
    })
    .then(result => {
        console.log(result);
        document.getElementById(original_id).innerHTML = edited_content;
        document.getElementById(form_id).style.display = 'none';
        document.getElementById(button_id).style.display = 'block';
        document.getElementById(original_id).style.display = 'block';
    });
}