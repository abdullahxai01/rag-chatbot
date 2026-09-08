const chatBox =
    document.getElementById("chat-box");

const userInput =
    document.getElementById("user-input");

const sendButton =
    document.getElementById("send-button");

const fileInput =
    document.getElementById("file-input");

const attachmentPreview =
    document.getElementById("attachment-preview");

const fileName =
    document.getElementById("file-name");

const fileType =
    document.getElementById("file-type");

const removeFile =
    document.getElementById("remove-file");


/* Add message */

function addMessage(message, type) {

    const messageDiv =
        document.createElement("div");

    messageDiv.classList.add("message");

    if (type === "user") {

        messageDiv.classList.add(
            "user-message"
        );

    } else {

        messageDiv.classList.add(
            "bot-message"
        );
    }

    messageDiv.textContent = message;

    chatBox.appendChild(messageDiv);

    chatBox.scrollTop =
        chatBox.scrollHeight;

    return messageDiv;
}


/* File selected */

fileInput.addEventListener(
    "change",
    function () {

        const file =
            fileInput.files[0];

        if (!file) {
            return;
        }

        fileName.textContent =
            file.name;

        fileType.textContent =
            `${file.type || "Document"} attached`;

        attachmentPreview.style.display =
            "flex";

        userInput.placeholder =
            "Ask something about this file...";

    }
);


/* Remove selected file */

removeFile.addEventListener(
    "click",
    function () {

        fileInput.value = "";

        attachmentPreview.style.display =
            "none";

        userInput.placeholder =
            "Ask a question...";

    }
);


/* Send */

async function sendMessage() {

    const question =
        userInput.value.trim();

    const file =
        fileInput.files[0];


    /*
     * Nothing entered and no file
     */

    if (!question && !file) {

        return;

    }


    /*
     * Disable button
     */

    sendButton.disabled = true;


    /*
     * FILE MODE
     */

    if (file) {

        addMessage(
            file.name,
            "user"
        );


        const thinkingMessage =
            addMessage(
                question
                    ? "Analyzing your document..."
                    : "Reading and summarizing your document...",
                "bot"
            );


        const formData =
            new FormData();

        formData.append(
            "file",
            file
        );


        try {

            /*
             * Send file to backend
             */

            const response =
                await fetch(
                    "http://127.0.0.1:8000/summarize",
                    {
                        method: "POST",

                        body: formData
                    }
                );


            if (!response.ok) {

                const errorData =
                    await response.json();

                throw new Error(
                    errorData.detail ||
                    "Failed to process document."
                );

            }


            const data =
                await response.json();


            /*
             * If user asked a question
             */

            if (question) {

                thinkingMessage.textContent =
                    "Document uploaded. " +
                    "Here is the document summary:\n\n" +
                    data.summary;

            } else {

                /*
                 * No question = complete summary
                 */

                thinkingMessage.textContent =
                    `Indexed ${data.chunks_indexed} chunks from ${data.filename}.\n\n` +
                    "Summary:\n\n" +
                    data.summary;

            }


            /*
             * Clear input
             */

            userInput.value = "";

            fileInput.value = "";

            attachmentPreview.style.display =
                "none";

            userInput.placeholder =
                "Ask a question...";


        } catch (error) {

            console.error(error);

            thinkingMessage.textContent =
                error.message ||
                "Unable to process the document.";

        }


        sendButton.disabled = false;

        return;
    }


    /*
     * NORMAL CHAT MODE
     */

    addMessage(
        question,
        "user"
    );

    userInput.value = "";


    const thinkingMessage =
        addMessage(
            "Thinking...",
            "bot"
        );


    try {

        const response =
            await fetch(
                "http://127.0.0.1:8000/chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        question: question
                    })
                }
            );


        if (!response.ok) {

            throw new Error(
                "Backend error"
            );

        }


        const data =
            await response.json();


        thinkingMessage.textContent =
            data.answer;


    } catch (error) {

        console.error(error);

        thinkingMessage.textContent =
            "Unable to connect to the chatbot backend.";

    }


    sendButton.disabled = false;

}


/* Send button */

sendButton.addEventListener(
    "click",
    sendMessage
);


/* Enter key */

userInput.addEventListener(
    "keydown",
    function (event) {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();

        }

    }
);