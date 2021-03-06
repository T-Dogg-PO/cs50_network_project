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


// Function for following / unfollowing
function followSave(profile_id) {
    // Send fetch request to the follow view
    fetch('/follow', {
        method: 'PUT',
        headers: { // Set the X-CSRFToken header to the csrf token obtained from getCookie
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({
            profile: profile_id,
        })
        
    })
    // Convert response from follow view to json
    .then(response => response.json())
    // Take the response data and update the follower_count without needing to reload the page
    .then(data => {
        document.getElementById('follower_count').innerHTML = data.total_followers;
    })
    .then(result => {
        console.log(result);
        // Update the follow/unfollow button
        if (document.getElementById('follow').style.display === 'none') {
            document.getElementById('follow').style.display = 'block';
            document.getElementById('unfollow').style.display = 'none';
        } else {
            document.getElementById('follow').style.display = 'none';
            document.getElementById('unfollow').style.display = 'block';
        }
        
    })
}


// Function for liking / unliking
function like(post_id) {
    let post_like_button = `${post_id}_like_button`;
    let post_likes = `${post_id}_likes`;
    fetch('/like', {
        method: 'PUT',
        headers: { // Set the X-CSRFToken header to the csrf token obtained from getCookie
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({
            post: post_id,
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById(post_likes).innerHTML = `${data.total_likes} likes`;
        if (data.user_like === true) {
            document.getElementById(post_like_button).innerHTML = 'Unlike';
        } else {
            document.getElementById(post_like_button).innerHTML = 'Like';
        }
    })
}