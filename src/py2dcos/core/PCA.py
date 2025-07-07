import os
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt


def process_excel_pca(excel_file_path, num_components, report_file="PCA_report.txt", save_plots=False):

    # Load the Excel file
    excel_data = pd.ExcelFile(excel_file_path)
    results = {}

    with open(report_file, "w") as rep:
        for sheet in excel_data.sheet_names:
            # Parse the sheet; header=1 assumes the header is in the second row, and decimal="," handles locale
            data = excel_data.parse(sheet, header=1, decimal=",")

            # Assume the first column contains wavelengths and the rest are spectral data
            wavelengths = data.iloc[:, 0].astype(float).values
            spectral_data = data.iloc[:, 1:].astype(float)

            # Center the data (subtract the mean of each column)
            data_centered = spectral_data - spectral_data.mean()

            pca = PCA()
            pca_result = pca.fit_transform(data_centered)
            explained_variance = pca.explained_variance_ratio_ * 100  # in percentages
            cumulative_variance = np.cumsum(explained_variance)

            # Write a report for this sheet
            rep.write(f"Sheet: {sheet}\n")
            rep.write("Explained Variance (%): " + str(explained_variance) + "\n")
            rep.write("Cumulative Variance (%): " + str(cumulative_variance) + "\n")
            rep.write(f"Reconstructing data using {num_components} principal components.\n")
            rep.write("-" * 40 + "\n\n")

            # Reconstruct the data using the first 'num_components' principal components.
            # This is done manually because inverse_transform expects the full score matrix.
            reconstructed_data = (np.dot(pca_result[:, :num_components],
                                         pca.components_[:num_components, :])
                                  + pca.mean_)

            # Optionally, generate and save a plot of the correlation matrix of the reconstructed data.
            if save_plots:
                corr_matrix = np.corrcoef(reconstructed_data.T)
                plt.figure(figsize=(10, 6))
                plt.imshow(corr_matrix, cmap='coolwarm', interpolation='nearest')
                plt.colorbar()
                plt.title(f"Correlation Matrix - {sheet}")
                plt.xlabel("Variables")
                plt.ylabel("Variables")
                plt.tight_layout()
                plot_filename = f"Correlation_{sheet}.png"
                plt.savefig(plot_filename)
                plt.close()
                rep.write(f"Saved correlation matrix plot as {plot_filename}\n\n")

            # Store the reconstructed data
            results[sheet] = reconstructed_data

    print(f"PCA report saved to {report_file}")
    return results


def main():
    # Set the path to your Excel file
    excel_file_path = "C://Users/julio/OneDrive - Escuela Superior Politécnica del Litoral/Py2DCOS - improved/data/Data for Base Case/Test1.xlsx"  # <-- change this to your file path
    # Specify the number of principal components for reconstruction
    num_components = 3  # change as needed

    # Process the Excel file, generate a PCA report, and obtain reconstructed data
    reconstructed_results = process_excel_pca(excel_file_path, num_components,
                                              report_file="PCA_report.txt", save_plots=True)

    # The reconstructed_results dictionary now holds the reconstructed data for each sheet.
    for sheet, matrix in reconstructed_results.items():
        print(f"Sheet: {sheet} - Reconstructed matrix shape: {matrix.shape}")


if __name__ == "__main__":
    main()
