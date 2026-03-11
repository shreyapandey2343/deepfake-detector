const API_PREDICT = "/predict";
const API_LOGIN = "/login";
const API_SIGNUP = "/signup";

// Demo mode for testing (set to true to use mock data)
const DEMO_MODE = false;

/* ===== UI SWITCH ===== */
function showSignup() {
    document.getElementById("loginBox").classList.add("hidden");
    document.getElementById("signupBox").classList.remove("hidden");
}

function showLogin() {
    document.getElementById("signupBox").classList.add("hidden");
    document.getElementById("loginBox").classList.remove("hidden");
}

/* ===== FILE INPUT HANDLER ===== */
document.getElementById("fileInput").addEventListener("change", function() {
    const fileName = this.files[0]?.name || "Choose Image";
    document.getElementById("fileText").innerText = "📂 " + fileName;
});

/* ===== SIGNUP ===== */
async function signup() {
    const email = document.getElementById("signupEmail").value;
    const password = document.getElementById("signupPassword").value;

    if (!email || !password) {
        alert("Please fill in all fields.");
        return;
    }

    try {
        const res = await fetch(API_SIGNUP, {
            method: "POST",
            body: new URLSearchParams({ email, password })
        });

        const data = await res.json();

        if (data.status === "ok") {
            alert("Signup successful. Please login.");
            showLogin();
        } else {
            alert(data.message || "Signup failed.");
        }
    } catch (error) {
        console.error("Signup error:", error);
        alert("Network error. Please try again.");
    }
}

/* ===== LOGIN ===== */
async function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    if (!email || !password) {
        alert("Please fill in all fields.");
        return;
    }

    try {
        const res = await fetch(API_LOGIN, {
            method: "POST",
            body: new URLSearchParams({ email, password })
        });

        const data = await res.json();

        if (data.status === "ok") {
            document.getElementById("loginBox").classList.add("hidden");
            document.getElementById("appBox").classList.remove("hidden");
        } else {
            alert(data.message || "Login failed.");
        }
    } catch (error) {
        console.error("Login error:", error);
        alert("Network error. Please try again.");
    }
}

/* ===== IMAGE ANALYSIS ===== */
async function analyze() {
    const fileInput = document.getElementById("fileInput");
    const analyzeBtn = document.getElementById("analyzeBtn");

    if (!fileInput.files.length) {
        alert("Please select an image first.");
        return;
    }

    /* Show loading state */
    analyzeBtn.disabled = true;
    analyzeBtn.innerText = "Analyzing...";

    const file = fileInput.files[0];
    const preview = document.getElementById("preview");
    preview.innerHTML = "";

    const img = document.createElement("img");
    img.src = URL.createObjectURL(file);
    preview.appendChild(img);

    const formData = new FormData();
    formData.append("file", file);

    try {
        let data;

        /* DEMO MODE - Use mock data for testing */
        if (DEMO_MODE) {
            await new Promise(resolve => setTimeout(resolve, 1500));
            const predictions = ["Fake", "Real", "Uncertain"];
            const randomPred = predictions[Math.floor(Math.random() * predictions.length)];
            data = {
                prediction: randomPred,
                confidence: Math.random() * 0.4 + 0.6
            };
            console.log("Demo mode - Mock data:", data);
        } else {
            /* REAL API CALL */
            const response = await fetch(API_PREDICT, {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            data = await response.json();
        }

        /* INVALID INPUT HANDLING */
        if (data.error) {
            document.getElementById("result").classList.remove("hidden");

            const label = document.getElementById("label");
            const confidence = document.getElementById("confidence");

            label.innerText = data.error;
            confidence.innerText = "";

            /* Clear flashcards */
            clearFlashcards();

            analyzeBtn.disabled = false;
            analyzeBtn.innerText = "Analyze Image";
            return;
        }

        /* SHOW RESULT */
        document.getElementById("result").classList.remove("hidden");

        const label = document.getElementById("label");
        const confidence = document.getElementById("confidence");

        label.innerText = `Prediction: ${data.prediction}`;
        confidence.innerText = `Confidence: ${(data.confidence * 100).toFixed(1)}%`;

        /* POPULATE OBSERVATION FLASHCARDS */
        populateObservationCards(data.prediction);

        /* POPULATE RISK FLASHCARDS (Only if Fake) */
        populateRiskCards(data.prediction);

        console.log("Analysis successful:", data);

    } catch (error) {
        console.error("Analysis error:", error);
        
        if (error.message.includes("404")) {
            alert("API endpoint not found. Please check if backend is running.");
        } else if (error.message.includes("Network")) {
            alert("Network error. Please check your connection.");
        } else {
            alert("Analysis failed. Please try again or enable demo mode.");
        }

        if (confirm("Backend API not responding? Enable demo mode for testing?")) {
            DEMO_MODE = true;
            alert("Demo mode enabled. You can now test without backend.");
        }
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.innerText = "Analyze Image";
    }
}

/* ===== POPULATE OBSERVATION CARDS ===== */
function populateObservationCards(prediction) {

    const obsCards = [
        document.getElementById("obsCard1"),
        document.getElementById("obsCard2"),
        document.getElementById("obsCard3"),
        document.getElementById("obsCard4")
    ];

    const obsBacks = document.querySelectorAll(".obs-back");

    /* Hide observations if prediction is not REAL */
    if (prediction !== "Real") {
        obsCards.forEach(card => card.style.display = "none");
        return;
    }

    /* Show observation cards */
    obsCards.forEach(card => card.style.display = "block");

    const observations = [
        "Natural skin texture patterns detected",
        "Consistent lighting across the face",
        "Facial landmarks align naturally",
        "No AI generation artifacts detected"
    ];

    obsBacks.forEach((back, index) => {
        back.innerText = observations[index];
    });

}
/* ===== POPULATE RISK CARDS (Only for Fake) ===== */


    function populateRiskCards(prediction) {

    const riskCards = [
        document.getElementById("riskCard1"),
        document.getElementById("riskCard2"),
        document.getElementById("riskCard3"),
        document.getElementById("riskCard4")
    ];

    const riskBacks = document.querySelectorAll(".risk-back");

    /* Hide risks if prediction is not FAKE */
    if (prediction !== "Fake") {
        riskCards.forEach(card => card.style.display = "none");
        return;
    }

    /* Show risk cards */
    riskCards.forEach(card => card.style.display = "block");

    const risks = [
        "Deepfake images can spread misinformation",
        "They may damage a person's reputation",
        "They can enable identity fraud",
        "They can manipulate political media"
    ];

    riskBacks.forEach((back, index) => {
        back.innerText = risks[index];
    });

}

/* ===== CLEAR FLASHCARDS ===== */
function clearFlashcards() {
    const obsBacks = document.querySelectorAll(".obs-back");
    const riskBacks = document.querySelectorAll(".risk-back");
    const riskCards = document.querySelectorAll(".risk-card");

    obsBacks.forEach(back => back.innerText = "");
    riskBacks.forEach(back => back.innerText = "");
    riskCards.forEach(card => card.style.display = "none");
}