'use strict'
const { merge } = require('webpack-merge')
const prodEnv = require('./prod.env')

module.exports = merge(prodEnv, {
  NODE_ENV: '"development"',
  VUE_APP_CESIUM_TOKEN: '"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIxN2IzODgxNi1hY2Y3LTQxYzItOTE2Zi0yNzEyMTVkOTM1Y2YiLCJpZCI6MzEyNDM0LCJpYXQiOjE3NTAwMzI3NzZ9.y4JQ6lZYz9q7QfRTTA-zI146Fv2J5FaGHPw0MDT0K8o"'
})
