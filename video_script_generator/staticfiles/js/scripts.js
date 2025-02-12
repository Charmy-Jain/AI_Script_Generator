document.getElementById("generateBtn").addEventListener("click", async () => {
    const outputDiv = document.getElementById("output");
    outputDiv.innerHTML = "<p class='text-gray-500'>Generating script... ⏳</p>";

    const prompt = document.getElementById("prompt").value;
    const vibe = document.getElementById("vibe").value;
    const videoFormat = document.getElementById("video_format").value;
    const externalLink = document.getElementById("externalLink").value;
    
    let extractedText = "";
    const fileInput = document.getElementById("fileInput");

    // Handle file upload
    if (fileInput.files.length > 0) {
        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        try {
            const fileResponse = await fetch("/upload_file/", {  // updated endpoint
                method: "POST",
                body: formData,
            });
            const fileData = await fileResponse.json();
            if (fileData.extracted_text) {
                extractedText = fileData.extracted_text.trim();
            }
        } catch (error) {
            outputDiv.innerHTML = `<p class='text-red-500'>Error uploading file: ${error.message}</p>`;
            return;
        }
    }

    // Handle external link metadata
    if (externalLink) {
        try {
            const linkResponse = await fetch("/fetch_metadata/", {  // endpoint matches
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: externalLink }),
            });
            const linkData = await linkResponse.json();
            if (linkData.metadata) {
                extractedText += " " + linkData.metadata.trim();
            }
        } catch (error) {
            outputDiv.innerHTML = `<p class='text-red-500'>Error fetching metadata: ${error.message}</p>`;
            return;
        }
    }

    // Generate the script
    try {
        const response = await fetch("/generate_script/", {  // updated endpoint
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt, vibe, video_format: videoFormat, extracted_text: extractedText }),
        });
        const data = await response.json();
        outputDiv.innerHTML = data.script 
            ? `<p class="p-4 bg-gray-100 rounded">${data.script.replace(/\n/g, "<br>")}</p>` 
            : `<span class="text-red-500">${data.error}</span>`;
    } catch (error) {
        outputDiv.innerHTML = `<p class='text-red-500'>Error generating script: ${error.message}</p>`;
    }
});
