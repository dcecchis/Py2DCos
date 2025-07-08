import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

class PCAProcessor:
    def __init__(self):
        pass
    
    def apply(self, data, n_components,
                                 report_filename="PCA_Report.txt",
                                 plot_correlogram=True, correlogram_filename='correlograma.png',
                                 plot_scores=True, scores_filename='scores.png'):

        if n_components <= 0:
            # No reconstruction requested – behave like the old code.
            return data.copy()


        # Center the data by subtracting column means.
        data_mean = data.mean()
        data_centered = data - data_mean

        pca = PCA(n_components=n_components)
        pca_result = pca.fit_transform(data_centered)

        # Reconstruct the data using the retained components.
        reconstructed = pca.inverse_transform(pca_result)
        reconstructed_df = pd.DataFrame(reconstructed, index=data.index, columns=data.columns)

        # Compute the correlation matrix of the reconstructed data.
        correlation_matrix = np.corrcoef(reconstructed_df.T)

        # Calculate explained variance statistics.
        explained_variance = pca.explained_variance_ratio_ * 100  # as percentages
        cumulative_variance = np.cumsum(explained_variance)

        # Generate a textual report.
        report_lines = []
        report_lines.append("PCA Report")
        report_lines.append("=" * 40)
        report_lines.append(f"Number of components used: {n_components}")
        report_lines.append("")
        report_lines.append("Explained Variance Ratio (%):")
        for i, ev in enumerate(explained_variance):
            report_lines.append(f"  PC{i + 1}: {ev:.2f}%")
        report_lines.append("")
        report_lines.append("Cumulative Variance (%):")
        for i, cv in enumerate(cumulative_variance):
            report_lines.append(f"  PCs 1 to {i + 1}: {cv:.2f}%")
        report_lines.append("")
        report_lines.append("Component Weights (Loadings):")
        for i, comp in enumerate(pca.components_):
            comp_str = ", ".join([f"{w:.4f}" for w in comp])
            report_lines.append(f"  PC{i + 1}: [{comp_str}]")
        report_text = "\n".join(report_lines)

        with open(report_filename, "w") as f:
            f.write(report_text)
        print(f"PCA report saved to {report_filename}")

        # Plot the correlogram (correlation matrix) if requested.
        if plot_correlogram:
            plt.figure(figsize=(8, 6))
            plt.imshow(correlation_matrix, cmap='coolwarm', interpolation='nearest')
            plt.colorbar()
            plt.title("Correlogram of Reconstructed Data")
            plt.xlabel("Variables")
            plt.ylabel("Variables")
            plt.tight_layout()
            if correlogram_filename:
                plt.savefig(correlogram_filename)
                print(f"Correlogram saved as {correlogram_filename}")
            else:
                plt.show()
            plt.close()

        # Plot the PCA scores if requested and if at least 2 components are available.
        if plot_scores:
            if n_components < 2:
                print("PCA scores plot not generated: need at least 2 components.")
            else:
                fig, ax = plt.subplots(figsize=(8, 6))

                # Plot the scores.
                ax.scatter(pca_result[:, 0], pca_result[:, 1], color='blue', marker='o')
                ax.set_xlabel(f"PC1 ({explained_variance[0]:.1f}% var)")
                ax.set_ylabel(f"PC2 ({explained_variance[1]:.1f}% var)")
                ax.set_title("PCA Scores Scatter Plot")

                ax.spines['left'].set_position('zero')
                ax.spines['bottom'].set_position('zero')
                ax.spines['right'].set_color('none')
                ax.spines['top'].set_color('none')

                # Add grid for clarity
                ax.grid(True, linestyle='--', alpha=0.5)

                threshold = np.percentile(np.abs(pca_result[:, 0]), 90)  # for example, top 10% in PC1
                for i, wavenumber in enumerate(data.index):
                    if abs(pca_result[i, 0]) > threshold or abs(pca_result[i, 1]) > threshold:
                        ax.annotate(str(wavenumber),
                                    (pca_result[i, 0], pca_result[i, 1]),
                                    fontsize=8,
                                    ha='center',
                                    va='center',
                                    color='darkred',
                                    xytext=(3, 3),
                                    textcoords='offset points')

                plt.tight_layout()
                if scores_filename:
                    plt.savefig(scores_filename)
                    print(f"PCA scores plot saved as {scores_filename}")

                plt.close()

        return reconstructed_df