from flask import Flask, Response, render_template, request, redirect, url_for, jsonify
import pandas as pd
import os
from plotting_functions import plottings
from model_trainer import ModelTrainer
from data_processor import DataProcessor
import openai
from groq import Groq

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
api_key = "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"

model_id = "mixtral-8x7b-32768"
client = Groq(api_key=api_key)

# Global değişkenler
data = None
numeric_columns = []
categorical_columns = []
table_html = None
scatter_plot_html = None
corr_table_html = None
categorical_plot_html = None
box_plot_html = None
train_results = None
chatgpt_analysis = None
previous_data_hash = None
columns = []

@app.route("/", methods=["GET", "POST"])
def upload_file():
    return render_template("index.html")

@app.route("/table", methods=["GET", "POST"])
def table_page():
    """
    CSV dosyasını yükler, veriyi işler ve tabloyu gösterir.
    """
    global data, numeric_columns, categorical_columns, table_html, scatter_plot_html, corr_table_html, categorical_plot_html, box_plot_html, columns

    # Dosyayı yükle veya önceden işlenmiş dosyayı oku
    process_data_path = os.path.join(app.config['UPLOAD_FOLDER'], "processed_data.csv")
    if request.method == "GET" and os.path.exists(process_data_path):
        data = pd.read_csv(process_data_path)
    elif request.method == "POST" and "file" in request.files:
        try:
            os.remove(process_data_path)
        except Exception as e:
            pass
        uploaded_file = request.files["file"]
        print(uploaded_file)
        if uploaded_file.filename.endswith(".csv"):
            data = pd.read_csv(uploaded_file)
        else:
            return render_template("table.html", error="Please upload a valid CSV file.", active_page="table")

    if data is None:
        return render_template("table.html", error="A valid CSV file has not been uploaded.", active_page="table")

    try:
        # Veriyi işle
        data_plottings = plottings(data)
        table_html = data.to_html(classes='table table-striped', index=False)
        numeric_columns = data.select_dtypes(include=["number"]).columns
        categorical_columns = data.select_dtypes(include=["object", "category"]).columns
        corr_table_html = data_plottings.correlation_matrix()
        categorical_plot_html = data_plottings.categorical_plot_html() if len(categorical_columns) > 0 else None
        box_plot_html = data_plottings.box_plot_to_html() if len(numeric_columns) > 0 else None
        columns = data.columns.to_list()
    except Exception as e:
        return render_template("table.html", error=f"An error occurred while processing the data: {str(e)}", active_page="table")

    return render_template("table.html", table=table_html, active_page="table")


@app.route("/scatter", methods=["GET", "POST"])
def scatter_page():
    """
    Sayısal sütun görünümü ve scatter matrix işlemleri aynı sayfada.
    """
    global scatter_plot_html

    if data is None:
        return render_template("scatter.html", active_page="scatter", error="Please select at least two columns!")

    if request.method == "POST":
        selected_columns = request.form.getlist("selected_columns")
        color_column = request.form.getlist("color_column")
        print(color_column)
        if not selected_columns or len(selected_columns) < 2:
            return render_template(
                "scatter.html",
                active_page="scatter",
                numeric_columns=numeric_columns,
                categorical_columns = categorical_columns,
                scatter_plot_html=None,
                error="Please select at least two columns!"
            )

        try:
            # Scatter matrix oluştur
            data_plottings = plottings(data)
            scatter_plot_html = data_plottings.scatter_matrix_to_html(selected_columns=selected_columns,color_column=color_column)
        except Exception as e:
            return render_template(
                "scatter.html",
                active_page="scatter",
                numeric_columns=numeric_columns,
                categorical_columns = categorical_columns,
                scatter_plot_html=None,
                error=f"An error occurred during visualization: {str(e)}"
            )

    return render_template(
        "scatter.html",
        active_page="scatter",
        numeric_columns=numeric_columns,
        categorical_columns = categorical_columns,
        scatter_plot_html=scatter_plot_html
    )
@app.route("/correlation", methods=["GET"])
def correlation_page():
    """
    Korelasyon matrisi sayfası
    """
    return render_template(
        "correlation.html",
        active_page="correlation",
        corr_table_html=corr_table_html
    )


@app.route("/categorical")
def categorical_page():
    """
    Kategorik sütun görünümü sayfası
    """
    return render_template(
        "categorical.html",
        active_page="categorical",
        categorical_plot_html=categorical_plot_html
    )


@app.route("/machine")
def machine_page():
    global train_results
    return render_template(
        "machine.html",
        active_page="machine",
        columns=columns,
        train_results=train_results
    )

@app.route("/train", methods=["POST"])
def train_model():
    global data, train_results

    if data is None:
        return render_template("index.html", error="Data not found. Please upload a file.")

    try:
        target_column = request.form.get("target_column")
        model_name = request.form.get("model")
        test_size = float(request.form.get("test_size", 0.2))
        model_parameter_value = request.form.get("model_parameter")

        if not target_column or not model_name:
            return render_template("index.html", error="A target column and model must be selected.")

        model_parameters = {key.replace("param_", ""): value for key, value in request.form.items() if key.startswith("param_")}
        if model_parameter_value:
            model_parameters["custom_param"] = model_parameter_value

        trainer = ModelTrainer(data, target_column, model_name, test_size, model_parameters)
        train_results = trainer.train_and_evaluate()
    except Exception as e:
        return render_template("index.html", error=f"An error occurred while training the model: {str(e)}")

    return redirect(url_for("machine_page"))

@app.route("/process_table", methods=["POST"])
def process_table():
    """
    Veriyi işler ve HTML tablosunu günceller.
    """
    global data

    if data is None:
        return jsonify({"error": "Data not found. Please upload a CSV file first."}), 400

    try:
        processor = DataProcessor(data)

        # Preprocessing seçeneklerini al
        missing_values_method = request.form.get("missing_values")
        normalization_method = request.form.get("normalization")
        encoding_method = request.form.get("encoding")
        column_name = request.form.get("column_name")
        row_index = request.form.get("row_index")

        # İşlemler
        if missing_values_method:
            processor.handle_missing_values(missing_values_method)
        if normalization_method:
            processor.normalize(normalization_method)
        if encoding_method:
            processor.encode_categorical(encoding_method)
        if column_name:
            processor.drop_column(column_name)
        if row_index:
            processor.drop_row(row_index)

        # İşlenmiş tabloyu döndür
        return data.to_html(classes='table table-striped', index=False)
    except Exception as e:
        return jsonify({"error": f"An error occurred:: {str(e)}"}), 500
    
@app.route("/ask_chatgpt", methods=["POST"])
def ask_chatgpt():
    """ ChatGPT API'si üzerinden otomatik analiz """
    global data, previous_data_hash, chatgpt_analysis, corr_table_html, train_results

    if data is None:
        return jsonify({"error": "The dataset is not available."}), 400

    # Dataset'in hash'ini hesapla
    current_data_hash = hash(pd.util.hash_pandas_object(data).sum())

    # Eğer dataset değiştiyse, yanıtı sıfırla
    if previous_data_hash != current_data_hash:
        previous_data_hash = current_data_hash
        chatgpt_analysis = None

    # Daha önce analiz yapıldıysa mevcut analizi döndür
    if chatgpt_analysis is not None:
        return jsonify({"analysis": chatgpt_analysis})

    try:
        # ChatGPT'ye gönderilecek mesaj
        messages = [
            {"role": "system", "content": "You are a Senior Data Analysis Engineer. Generate insights about the dataset based on the information provided by the user.\
              Make your answers detailed and explanatory. Do not include tables in your responses."},
            {"role": "user", "content": f"""
                Automatic analysis of the dataset::
                - Number of rows: {len(data)}
                - Columns: {', '.join(data.columns)}
                - Correlation matrix: {corr_table_html if corr_table_html else 'Not available'}
                - Training results: {train_results if train_results else 'Training not yet performed'}
            """}
        ]
        # ChatGPT API çağrısı
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=model_id,
            temperature=1.0,
            max_tokens=300,
        )
        chatgpt_analysis = chat_completion.choices[0].message.content.strip()
        print(chatgpt_analysis)
        return jsonify({"analysis": chatgpt_analysis})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# Dashboard rotası

@app.route("/chatgpt_dashboard")
def chatgpt_dashboard():
    global data, corr_table_html, train_results

    return render_template(
        "chatgpt_dashboard.html",
        active_page="chatgpt_dashboard",
        data_loaded=(data is not None),
        corr_matrix=corr_table_html,
        train_results=train_results,
        columns=data.columns.to_list() if data is not None else None
    )


@app.route("/save_and_refresh_all", methods=["POST"])
def save_and_refresh_all():
    """
    Tüm sayfaların bilgilerini tablo düzenlemeleri sonrası günceller.
    """
    global data, numeric_columns, categorical_columns, scatter_plot_html, corr_table_html, categorical_plot_html, box_plot_html, columns

    if data is None:
        return jsonify({"message": "No data available to save."}), 400

    try:
        # Veriyi kaydet
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], "processed_data.csv")
        data.to_csv(save_path, index=False)

        # Tüm sayfa bilgilerini güncelle
        numeric_columns = data.select_dtypes(include=["number"]).columns.tolist()
        categorical_columns = data.select_dtypes(include=["object", "category"]).columns.tolist()
        
        data_plottings = plottings(data)
        corr_table_html = data_plottings.correlation_matrix()
        categorical_plot_html = data_plottings.categorical_plot_html() if len(categorical_columns) > 0 else None
        box_plot_html = data_plottings.box_plot_to_html() if len(numeric_columns) > 0 else None
        columns = data.columns.to_list()

        return jsonify({"message": "All pages have been successfully updated!"}), 200
    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

@app.route("/download_table", methods=["GET"])
def download_table():
    """
    Düzenlenmiş tabloyu CSV formatında indirilebilir hale getirir.
    """
    global data

    if data is None:
        return jsonify({"error": "No table available for download. Please create a table first."}), 400

    try:
        # Veriyi CSV formatına dönüştür
        csv_data = data.to_csv(index=False)

        # Türkçe karakterlerden arındırılmış bir dosya adı kullanın
        filename = "duzenlenmis_tablo.csv"

        # Response olarak gönder
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename={filename}"}
        )
    except Exception as e:
        return jsonify({"error": f"An error occurred while downloading the table: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)