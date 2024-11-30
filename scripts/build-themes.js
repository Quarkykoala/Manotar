const less = require('less');
const fs = require('fs');
const path = require('path');
const CleanCSS = require('less-plugin-clean-css');

// Fix paths to use mental-health-dashboard directory
const rootDir = path.resolve(__dirname, '..');
const nodeModulesPath = path.resolve(rootDir, 'node_modules');
const themePath = path.resolve(rootDir, 'src', 'styles', 'themes', 'main.less');
const outputPath = path.resolve(rootDir, 'public', 'themes', 'main.css');

// Ensure the output directory exists
const outputDir = path.dirname(outputPath);
if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
}

console.log('Starting theme compilation...');
console.log('Node modules path:', nodeModulesPath);
console.log('Theme path:', themePath);
console.log('Output path:', outputPath);

// Read the LESS file
const lessContent = fs.readFileSync(themePath, 'utf8');

// Compile LESS to CSS
less.render(lessContent, {
    filename: themePath,
    paths: [
        nodeModulesPath,
        path.resolve(rootDir, 'src', 'styles', 'themes')
    ],
    plugins: [new CleanCSS({ advanced: true })],
    javascriptEnabled: true,
    math: 'always',
    modifyVars: {
        'primary-color': '#0059AB',
        'link-color': '#1890ff',
        'success-color': '#52c41a'
    },
    sourceMap: {
        sourceMapFileInline: true
    }
})
.then(output => {
    // Create the output directory if it doesn't exist
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // Write the CSS file
    fs.writeFileSync(outputPath, output.css);
    console.log('✨ Theme compiled successfully!');
    console.log('Output file:', outputPath);
})
.catch(error => {
    console.error('🚨 Error compiling theme:');
    console.error('Error details:', error.message);
    console.error('File:', error.filename);
    console.error('Line:', error.line);
    console.error('Column:', error.column);
    process.exit(1);
});
