document.getElementById('expressionForm').addEventListener('submit', handleSubmit);
document.getElementById('tacForm').addEventListener('submit', handleSubmit);

async function handleSubmit(e) {
    e.preventDefault();
    
    const isExpression = e.target.id === 'expressionForm';
    const input = isExpression ? 
        document.getElementById('expressionInput').value :
        document.getElementById('tacInput').value;
    
    const dagImage = document.getElementById('dagImage');
    const analysisResults = document.getElementById('analysisResults');
    
    // Show loading state
    dagImage.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
    analysisResults.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
    
    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                input_type: isExpression ? 'expression' : 'tac',
                input_data: input
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Display the DAG image
        dagImage.innerHTML = `<img src="data:image/png;base64,${data.image}" alt="DAG Visualization">`;
        
        // Display analysis results
        let resultsHtml = '<div class="alert alert-success">';
        resultsHtml += `<p><strong>Minimum number of registers required:</strong> ${data.min_registers}</p>`;
        
        if (isExpression) {
            resultsHtml += '<p><strong>Generated Three-Address Code:</strong></p>';
            resultsHtml += '<pre>' + data.tac_instructions.join('\n') + '</pre>';
        }
        
        resultsHtml += '<p><strong>Node Details:</strong></p>';
        resultsHtml += '<pre>' + data.node_details + '</pre>';
        resultsHtml += '</div>';
        analysisResults.innerHTML = resultsHtml;
        
    } catch (error) {
        dagImage.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
        analysisResults.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
    }
} 