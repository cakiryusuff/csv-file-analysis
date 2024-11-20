from sklearn.preprocessing import LabelEncoder
import pandas as pd
import plotly.express as px

class plottings():
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.numeric_columns = data.select_dtypes(include=["number"]).columns
        self.categorical_columns = data.select_dtypes(include=["object", "category"]).columns

    def correlation_matrix(self) -> str:

        # Kategorik sütunları kodlamak
        encoded_data = self.data.copy()
        for col in self.categorical_columns:
            le = LabelEncoder()
            encoded_data[col] = le.fit_transform(encoded_data[col].astype(str))

        # Sayısal + Kategorik Sütunlar Korelasyon Matrisi
        all_columns = list(self.numeric_columns) + list(self.categorical_columns)
        corr_matrix = encoded_data[all_columns].corr()

        # Korelasyon Matrisi Tablosunu HTML'ye Dönüştürmek
        corr_table_html = corr_matrix.to_html(classes='table table-striped table-bordered', float_format="{:.2f}".format)

        corr_table_html = f"""
        <div class="table-container">
            {corr_table_html}
        </div>
        """
        return corr_table_html

    def scatter_matrix_to_html(self, selected_columns, color_column = None) -> str:
        """
        Scatter Matrix grafiğini HTML formatında döner.

        Args:
            selected_columns (list): Kullanılacak sayısal sütunlar.
            color_column (str, optional): Noktaları renklendirmek için kullanılacak kategorik sütun.

        Returns:
            str: Scatter Matrix grafiğinin HTML formatı.
        """
        if color_column[0] is None or color_column[0] == '':
            fig_numeric = px.scatter_matrix(
                            self.data,
                            dimensions=selected_columns,  # İlk 4 sayısal sütunu kullan
                            color_discrete_sequence=px.colors.qualitative.Set1,  # Renk paleti
                            title="Colored Numerical Column Scatter Matrix",
                            labels={col: col for col in self.numeric_columns},
                        )
        else:
            fig_numeric = px.scatter_matrix(
                            self.data,
                            dimensions=selected_columns,  # İlk 4 sayısal sütunu kullan
                            color_discrete_sequence=px.colors.qualitative.Set1,  # Renk paleti
                            title="Colored Numerical Column Scatter Matrix",
                            color=self.data[color_column[0]],
                            labels={col: col for col in self.numeric_columns},
                        )
        fig_numeric.update_layout(
                        autosize=False,
                        width=1000,
                        height=700,
                        margin=dict(l=20, r=20, t=40, b=20),
                    )
        numeric_plot_html = fig_numeric.to_html(full_html=False)
        return numeric_plot_html

    def categorical_plot_html(self):
            fig_categorical = px.bar(
                    self.data,
                    x=self.categorical_columns[0],  # İlk kategorik sütunu kullan
                    color=self.categorical_columns[0],  # Kategorik sütuna göre renklendir
                    color_discrete_sequence=px.colors.qualitative.Pastel,  # Pastel renk paleti
                    title=f"Categorical Column: Distribution of {self.categorical_columns[0]}",
                    labels={self.categorical_columns[0]: "Categories"},
                )
            fig_categorical.for_each_trace(lambda trace: trace.update(visible="legendonly"))
            fig_categorical.update_layout(
                    autosize=False,
                    width=800,
                    height=500,
                    margin=dict(l=20, r=20, t=40, b=20),
                )
            categorical_plot_html = fig_categorical.to_html(full_html=False)
            return categorical_plot_html

    def box_plot_to_html(self) -> str:
        melted_data = self.data.melt(value_vars=self.numeric_columns, var_name="Columns", value_name="Values")
        fig_boxplot = px.box(
            melted_data,
            x="Columns",  # Sütun isimlerini x ekseninde göster
            y="Values",  # Değerleri y ekseninde göster
            points="all",  # Aykırı değerleri göster
            color="Columns",  # Her sütunu farklı renklendir
            color_discrete_sequence=px.colors.qualitative.Pastel,  # Pastel renk paleti
            title="Tüm Columns için Boxplot",
            labels={"Columns": "Columns", "Values": "Values"},
        )
        fig_boxplot.for_each_trace(lambda trace: trace.update(visible="legendonly"))
        fig_boxplot.update_layout(
            autosize=False,
            width=1000,
            height=600,
            margin=dict(l=20, r=20, t=40, b=20),
        )
        boxplot_html = fig_boxplot.to_html(full_html=False)
        return boxplot_html