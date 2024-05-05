import json

def process_coverage_summary(json_file, summary_file):
    with open(json_file, 'r') as f:
        coverage_data = json.load(f)

    summary = {
        'meta': {
            'version': coverage_data['meta']['version'],
            'timestamp': coverage_data['meta']['timestamp'],
            'branch_coverage': False,
            'show_contexts': False
        },
        'totals': {
            'covered_lines': coverage_data['totals']['covered_lines'],
            'num_statements': coverage_data['totals']['num_statements'],
            'percent_covered': coverage_data['totals']['percent_covered'],
            'missing_lines': coverage_data['totals']['missing_lines'],
            'excluded_lines': coverage_data['totals']['excluded_lines']
        }
    }

    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

if __name__ == '__main__':
    json_file = './coverage.json'
    summary_file = './coverage_summary.json'
    process_coverage_summary(json_file, summary_file)