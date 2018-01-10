module.exports = {
    siteMetadata: {
      title: `lulzgif`,
    },
    plugins: [
      {
        resolve: `gatsby-source-filesystem`,
        options: {
          name: `src`,
          path: `${__dirname}/public/static/`,
        },
      },
      `gatsby-plugin-react-helmet`
    ],
  }