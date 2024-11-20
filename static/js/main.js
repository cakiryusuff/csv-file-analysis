document.addEventListener("DOMContentLoaded", () => {
askChatGPT();
});

function askChatGPT() {
    const chatBox = document.getElementById("chat-box");

    // API çağrısı
    fetch("/ask_chatgpt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({})
    })
        .then(response => response.json())
        .then(data => {
            const botMessage = document.createElement("div");
            botMessage.className = "message bot-message";
            botMessage.textContent = data.analysis || data.error || "Bir sorun oluştu.";
            chatBox.appendChild(botMessage);
        })
        .catch(error => {
            console.error("API hatası:", error);
            const errorMessage = document.createElement("div");
            errorMessage.className = "message bot-message";
            errorMessage.textContent = "Bir hata oluştu. Lütfen tekrar deneyin.";
            chatBox.appendChild(errorMessage);
        });
}

document.getElementById("applyProcessing")?.addEventListener("click", () => {
    const formData = new FormData(document.getElementById("processingForm"));
    fetch("/process", {
        method: "POST",
        body: formData
    })
    .then(response => response.text())
    .then(data => {
        document.getElementById("dataTable").innerHTML = data;
    })
    .catch(error => {
        console.error("Hata:", error);
    });
});

document.getElementById("saveData")?.addEventListener("click", () => {
    fetch("/save_and_reload", { method: "POST" })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        } else {
            return response.json();
        }
    })
    .then(data => {
        if (data && data.message) {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error("Kaydetme ve yeniden yükleme sırasında hata oluştu:", error);
    });
});
document.getElementById("applyProcessing").addEventListener("click", () => {
const form = document.getElementById("tableProcessingForm");
const formData = new FormData(form);

fetch("/process_table", {
    method: "POST",
    body: formData
})
.then(response => {
    if (!response.ok) {
        throw new Error("Tablo işleme sırasında hata oluştu.");
    }
    return response.text();
})
.then(data => {
    document.getElementById("updatedTable").innerHTML = `
        <h3>Güncellenmiş Tablo</h3>
        <div class="table-responsive">${data}</div>
    `;

    // Form alanlarını sıfırla
    form.reset();
})
.catch(error => {
    console.error("Hata:", error);
    alert("Bir hata oluştu. Lütfen tekrar deneyin.");
});
});

document.getElementById("saveAndRefreshAll").addEventListener("click", () => {
fetch("/save_and_refresh_all", {
    method: "POST"
})
.then(response => {
    if (!response.ok) {
        throw new Error("Kaydetme ve yenileme sırasında hata oluştu.");
    }
    return response.json();
})
.then(data => {
    if (data.message) {
        alert(data.message);
        // Sayfayı tamamen yenile
        window.location.reload();
    }
})
.catch(error => {
    console.error("Hata:", error);
    alert("Bir hata oluştu. Lütfen tekrar deneyin.");
});
});

function showCustomParameter(selectElement) {
const modelType = selectElement.value; // Seçilen model tipi (classifier, regression, clustering)
const machineLearningModel = document.getElementById("machineLearningModel");
const paramField = document.getElementById("customParameterField");
const paramLabel = document.getElementById("paramLabel");
const targetColumnField = document.getElementById("targetColumnField");
const testValueField = document.getElementById("testValueField");

// Modele göre dinamik parametreler
const modelParams = {
classifier: {
    "Logistic Regression Classifier": "max_iter",
    "Decision Tree Classifier": "criterion",
    "Random Forest Classifier": "n_estimators",
    "Support Vector Machine Classifier": "kernel",
    "K-Nearest Neighbors Classifier": "n_neighbors",
    "Naive Bayes Classifier": ""
},
regression: {
    "Linear Regression": "normalize",
    "Random Forest Regression": "n_estimators"
},
clustering: {
    "K-Means Clustering": "n_clusters",
    "DBSCAN": "eps"
}
};

// Eğer model tipi seçilmişse ilgili alanları göster
if (modelType && modelParams[modelType]) {
// Seçilen model tipine uygun modelleri dinamik olarak doldur
const modelDropdown = document.getElementById("machine_model");
modelDropdown.innerHTML = '<option value="" disabled selected>Model Seçiniz</option>'; // Önce sıfırla

// Modelleri dropdown'a ekle
for (const [model, param] of Object.entries(modelParams[modelType])) {
    const option = document.createElement("option");
    option.value = model;
    option.textContent = model;
    modelDropdown.appendChild(option);
}

// Model seçim dropdown'unu göster
machineLearningModel.style.display = "block";

// Classification ve Regression için hedef sütun ve test oranı alanlarını göster
if (modelType === "classifier" || modelType === "regression") {
    targetColumnField.style.display = "block";
    testValueField.style.display = "block";
} else {
    targetColumnField.style.display = "none";
    testValueField.style.display = "none";
}

// Parametre alanını gizle (Model seçildiğinde tekrar gösterilir)
paramField.style.display = "none";
} else {
// Model tipi seçilmemişse tüm alanları gizle
machineLearningModel.style.display = "none";
paramField.style.display = "none";
targetColumnField.style.display = "none";
testValueField.style.display = "none";
}
}

// Ek fonksiyon: Model seçildiğinde parametre alanını göster
function showModelParameter(selectElement) {
const selectedModel = selectElement.value;
const paramField = document.getElementById("customParameterField");
const paramLabel = document.getElementById("paramLabel");

// Seçilen modelin parametre tanımı
const modelParams = {
"Logistic Regression Classifier": "max_iter",
"Decision Tree Classifier": "criterion",
"Random Forest Classifier": "n_estimators",
"Support Vector Machine Classifier": "kernel",
"K-Nearest Neighbors Classifier": "n_neighbors",
"Naive Bayes Classifier": "",
"Linear Regression": "",
"Random Forest Regression": "n_estimators",
"K-Means Clustering": "n_clusters",
"DBSCAN": "eps"
};

// Parametre varsa göster, yoksa gizle
if (selectedModel && modelParams[selectedModel]) {
paramLabel.innerText = `Model Parametresi (${modelParams[selectedModel]}):`;
paramField.style.display = "block";
} else {
paramField.style.display = "none";
}
}