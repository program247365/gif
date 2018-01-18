import React from "react"
import {Helmet} from "react-helmet";
import { withPrefix } from 'gatsby-link';

export default ({ data }) => {
  return (
    <article style={{color: "#4D4D4F"}} className="bg-light-yellow">
        <Helmet>
            <meta charSet="utf-8" />
            <title>Lulz Gif Party! (Beta) 🎉</title>
            <meta name="viewport" content="width=device-width, initial-scale=1"/>
            <link rel="stylesheet" href="https://unpkg.com/tachyons/css/tachyons.min.css"/>
            <script src="https://unpkg.com/lazysizes@4.0.1/lazysizes.min.js" async=""/>
        </Helmet>
        <h2 className="w-100 center avenir tc-l ph3 ph4-ns pt4 center">🎉 Lulz Gif Party! 🎉</h2>
        <div className="cf pa2">
            {data.allFile.edges.map(({ node }, index) =>
                <div className="fl w-50 w-25-m w-20-l pa2" key={index}>
                    <a href={__PATH_PREFIX__ + node.relativePath} className="db link dim tc">
                        { /*
                            <button className={index + 'copyme'}>{location.href + '/i/' + node.relativePath}</button>
                            todo create copy of image url
                            using https://clipboardjs.com/
                        */}
                        <img data-src={__PATH_PREFIX__ + node.relativePath} alt={node.name + '.' + node.extension} className="lazyload w-100 db outline black-10 grow"/>
                        <dl className="mt2 f6 lh-copy">
                            <dd className="ml0 black truncate w-100" data-clipboard-target={index + 'copyme'}>{node.name + '.' + node.extension}</dd>
                            <dd className="ml0 gray truncate w-100">{node.prettySize}</dd>
                        </dl>
                    </a>
                </div>
            )}
        </div>
    </article>
  )
}

export const query = graphql`
  query MyFilesQuery {
    allFile {
      edges {
        node {
          name
          relativePath
          prettySize
          extension
          birthTime(fromNow: true)
        }
      }
    }
  }
`