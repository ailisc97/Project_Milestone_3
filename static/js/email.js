/* Function for contact form to send email with 
    contact form contents to site owner */
    function sendMail(contactForm) {
        emailjs.send("gmail", "ms3", {
            "from_name": contactForm.name.value,
            "from_email": contactForm.email.value,
            "comments": contactForm.comments.value
        })
        .then(
            function() {
                $('.email-response').html("Thank you for your email, someone will be in touch shortly.");
            },
            function() {
                $('.email-response').html("There was an error with our email service. Please try again in a few minutes.");
            }
        );
        // Reset Form data
        document.getElementById("contact-form").reset();
        return false;
    }