from flask import Flask, render_template, request, redirect, url_for
import numpy as np

app = Flask(__name__)

criteria = []

# LANDING PAGE / HOME
@app.route('/')
def home():
    return render_template('home.html')

# MANAGE KRITERIA
@app.route('/kriteria')
def kriteria():
    return render_template('kriteria.html', criteria=criteria)

@app.route('/add_criteria', methods=['POST'])
def add_criteria():
    if request.method == 'POST':
        new_criterion = request.form['name']
        criteria.append({"id": len(criteria)+1, "name": new_criterion})
    return redirect(url_for('kriteria'))

@app.route('/delete_criteria/<int:id>', methods=['POST', 'DELETE'])
def delete_criteria(id):
    if request.method in ['POST', 'DELETE']:
        for criterion in criteria:
            if criterion['id'] == id:
                criteria.remove(criterion)
                break
    return redirect(url_for('kriteria'))

#MANAGE BOBOT KRITERIA
@app.route('/bobotkriteria')
def bobotkriteria():
    criterion_count = len(criteria)
    return render_template('bobotkriteria.html', criteria=criteria, criterion_count=criterion_count)

@app.route('/set_comparison', methods=['POST'])
def set_comparison():
    if request.method == 'POST':
        comparison_matrix = np.zeros((len(criteria), len(criteria)))
        for i in range(len(criteria)):
            for j in range(len(criteria)):
                if i != j:
                    comparison_value = float(request.form[f'comparison_{i}_{j}'])
                    comparison_matrix[i][j] = comparison_value
                    comparison_matrix[j][i] = 1 / comparison_value
        criteria_weights = calculate_ahp_weights(comparison_matrix)
        for i, weight in enumerate(criteria_weights):
            criteria[i]['weight'] = weight
    return redirect(url_for('bobotkriteria'))

def calculate_ahp_weights(comparison_matrix):
    n = len(comparison_matrix)
    eigenvalues, eigenvectors = np.linalg.eig(comparison_matrix)
    max_eigenvalue_index = np.argmax(eigenvalues)
    principal_eigenvector = np.real(eigenvectors[:, max_eigenvalue_index])
    weights = principal_eigenvector / np.sum(principal_eigenvector)
    return weights

# MANAGE ALTERNATIF

alternatives = []

@app.route('/alternatif')
def alternatif():
    return render_template('alternatif.html', alternatives=alternatives)

@app.route('/add_alternative', methods=['POST'])
def add_alternative():
    if request.method == 'POST':
        new_alternative = request.form['name']
        alternatives.append({"id": len(alternatives)+1, "name": new_alternative})
    return redirect(url_for('alternatif'))

@app.route('/delete_alternative/<int:id>', methods=['POST', 'DELETE'])
def delete_alternative(id):
    if request.method in ['POST', 'DELETE']:
        for alternative in alternatives:
            if alternative['id'] == id:
                alternatives.remove(alternative)
                break
    return redirect(url_for('alternatif'))

# MANAGE BOBOT ALTERNATIF

@app.route('/bobotalternatif')
def bobotalternatif():
    return render_template('bobotalternatif.html', alternatives=alternatives, criteria=criteria)

@app.route('/set_alternative_scores', methods=['POST'])
def set_alternative_scores():
    if request.method == 'POST':
        for alternative in alternatives:
            alternative_scores = {}
            for criterion in criteria:
                score_key = f"score_{alternative['id']}_{criterion['id']}"
                score = float(request.form.get(score_key, 0))
                alternative_scores[criterion['id']] = score
            alternative['scores'] = alternative_scores
    return redirect(url_for('bobotalternatif'))

# MANAGE KALKULASI

@app.route('/kalkulasi')
def kalkulasi():
    calculate_criteria_priority_weights()
    calculate_alternative_priority_weights()
    ranked_alternatives = perform_ranking()
    return render_template('kalkulasi.html', criteria=criteria, alternatives=alternatives, ranked_alternatives=ranked_alternatives)

def calculate_criteria_priority_weights():
    for criterion in criteria:
        criterion['row_total'] = sum(criterion['normalized_matrix'])

    for criterion in criteria:
        total = criterion['row_total']
        criterion['normalized_matrix'] = [cell / total for cell in criterion['normalized_matrix']]
        criterion['weight'] = sum(criterion['normalized_matrix']) / len(criteria)

def calculate_alternative_priority_weights():
    for alternative in alternatives:
        weights = []
        for criterion in criteria:
            weights.append(alternative['scores'][criterion['id']] * criterion['weight'])
        alternative['weight'] = sum(weights) / len(criteria)

def perform_ranking():
    ranked_alternatives = sorted(alternatives, key=lambda x: x['weight'], reverse=True)
    return ranked_alternatives

if __name__ == '__main__':
    app.run(debug=True)
