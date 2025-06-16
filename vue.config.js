module.exports = {
  devServer: {
    proxy: {
      '/opencache.statkart.no': {
        target: 'https://opencache.statkart.no',
        changeOrigin: true,
        pathRewrite: {
          '^/opencache.statkart.no': ''
        }
      }
    }
  }
} 