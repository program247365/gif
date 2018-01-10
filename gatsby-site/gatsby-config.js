module.exports = {
    siteMetadata: {
      title: `lulzgif`,
    },
    plugins: [
      {
        resolve: `gatsby-source-filesystem`,
        options: {
          name: `src`,
          path: `${__dirname}/static/`,
        },
      },
      `gatsby-plugin-react-helmet`
    ],
  }