const fs = require('fs');
const path = require('path');

function generateErrorReport(outputFile) {
  const errorTracker = require('../src/utils/errorTracker').errorTracker;
  const report = errorTracker.generateReport();
  
  const fullReport = {
    timestamp: new Date().toISOString(),
    summary: report,
    errors: errorTracker.getUnresolvedErrors(),
    recommendations: generateRecommendations(report)
  };

  fs.writeFileSync(outputFile, JSON.stringify(fullReport, null, 2));
  console.log(`Error report generated: ${outputFile}`);
}

function generateRecommendations(report) {
  const recommendations = [];
  
  // Check setup errors
  if (report.byType.setup > 0) {
    recommendations.push({
      priority: 'HIGH',
      message: 'Fix setup issues first as they may affect other tests',
      affected: 'Setup phase'
    });
  }

  // Check component with most errors
  const worstComponent = Object.entries(report.byComponent)
    .sort(([,a], [,b]) => b - a)[0];
  if (worstComponent) {
    recommendations.push({
      priority: 'HIGH',
      message: `Focus on fixing ${worstComponent[0]} component which has ${worstComponent[1]} errors`,
      affected: worstComponent[0]
    });
  }

  return recommendations;
}

// Parse command line arguments
const args = process.argv.slice(2);
const outputArg = args.find(arg => arg.startsWith('--output='));
if (outputArg) {
  const outputFile = outputArg.split('=')[1];
  generateErrorReport(outputFile);
} else {
  console.error('Please specify output file with --output=<filename>');
  process.exit(1);
}
