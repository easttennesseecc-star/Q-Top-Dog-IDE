// Jest transform for SVG imports (CommonJS)
module.exports = {
  process() {
    return {
      code: 'module.exports = "svg-mock";',
    };
  },
};