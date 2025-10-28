// Jest transform for SVG imports
module.exports = {
  process() {
    return {
      code: 'module.exports = "svg-mock";',
    };
  },
};