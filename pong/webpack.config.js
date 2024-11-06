const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  entry: './src/main.js',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist'),
    clean: true, // Clean the output directory before emit
  },
  mode: 'development', // Use development mode
  plugins: [
    new HtmlWebpackPlugin({
      template: './src/index.html',
    }),
  ],
  devServer: {
    static: {
      directory: path.join(__dirname, 'dist'),
    },
    compress: true,
    port: 9000,
    open: true, // Automatically open the browser
    hot: true, // Enable Hot Module Replacement
  },
  resolve: {
    alias: {
      three: path.resolve('./node_modules/three'),
    },
  },
  performance: {
    hints: false, // Disable performance hints
  },
  cache: false, // Disable caching
};
