import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

class PCAProcessor:
    def __init__(self):
        # no initialization state required for pca processing
        pass
    
    def apply(self, data, n_components,
                                 report_filename="PCA_Report.txt",
                                 plot_correlogram=True, correlogram_filename='correlograma.png',
                                 plot_scores=True, scores_filename='scores.png'):
        # if user did not request any components, skip pca and return a safe copy
        if n_components <= 0:
            return data.copy()

        # subtract mean per column so that principal components capture variance around zero
        data_mean = data.mean()
        data_centered = data - data_mean

        # perform pca to reduce dimensions
        pca = PCA(n_components=n_components)
        pca_result = pca.fit_transform(data_centered)

        # reconstruct data back in original space for comparison or further use
        reconstructed = pca.inverse_transform(pca_result)
        reconstructed_df = pd.DataFrame(
            reconstructed,
            index=data.index,
            columns=data.columns
        )

        # compute correlation matrix of reconstructed data for correlogram visualization
        correlation_matrix = np.corrcoef(reconstructed_df.T)

        # calculate explained variance percentages for each component
        explained_variance = pca.explained_variance_ratio_ * 100
        # cumulative sum helps see how much variance is captured up to each pc
        cumulative_variance = np.cumsum(explained_variance)

        # build a human-readable report of pca results
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

        # write report to file so user can review detailed pca metrics
        with open(report_filename, "w") as f:
            f.write(report_text)
        print(f"PCA report saved to {report_filename}")

        # if correlogram requested, plot and save or display it
        if plot_correlogram:
            plt.figure(figsize=(8, 6))
            plt.imshow(correlation_matrix, cmap='coolwarm', interpolation='nearest')
            plt.colorbar()
            plt.title("Correlogram of Reconstructed Data")
            plt.xlabel("Variables")
            plt.ylabel("Variables")
            plt.tight_layout()
            if correlogram_filename:
                # save image for later inspection
                plt.savefig(correlogram_filename)
                print(f"Correlogram saved as {correlogram_filename}")
            else:
                plt.show()
            plt.close()

        # if scatter of scores requested and at least two components available
        if plot_scores:
            if n_components < 2:
                # skip plot when insufficient dimensions for a 2d scatter
                print("PCA scores plot not generated: need at least 2 components.")
            else:
                fig, ax = plt.subplots(figsize=(8, 6))
                # plot first two principal component scores to visualize sample distribution
                ax.scatter(pca_result[:, 0], pca_result[:, 1], marker='o')
                ax.set_xlabel(f"PC1 ({explained_variance[0]:.1f}% var)")
                ax.set_ylabel(f"PC2 ({explained_variance[1]:.1f}% var)")
                ax.set_title("PCA Scores Scatter Plot")

                # reposition axes lines through origin for reference
                ax.spines['left'].set_position('zero')
                ax.spines['bottom'].set_position('zero')
                ax.spines['right'].set_color('none')
                ax.spines['top'].set_color('none')

                # add grid to help read point positions
                ax.grid(True, linestyle='--', alpha=0.5)

                # annotate outliers in top 10% by absolute score value
                threshold = np.percentile(np.abs(pca_result[:, 0]), 90)
                for i, label in enumerate(data.index):
                    if abs(pca_result[i, 0]) > threshold or abs(pca_result[i, 1]) > threshold:
                        ax.annotate(
                            str(label),
                            (pca_result[i, 0], pca_result[i, 1]),
                            fontsize=8,
                            ha='center',
                            va='center',
                            xytext=(3, 3),
                            textcoords='offset points'
                        )

                plt.tight_layout()
                if scores_filename:
                    # save the scores scatter plot for further review
                    plt.savefig(scores_filename)
                    print(f"PCA scores plot saved as {scores_filename}")
                plt.close()

        # return reconstructed dataframe so downstream code can continue
        return reconstructed_df
