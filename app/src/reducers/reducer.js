import { Value } from 'slate';
import * as actions from '../constants/action_types';

//const algorithmDescription = Value.fromJSON({
  //document: {
    //nodes: [
      //{
        //object: 'block',
        //type: 'paragraph',
        //nodes: [
          //{
            //object: 'text',
            //leaves: [
              //{
                //text: 'A line of text in a paragraph.',
              //},
            //],
          //},
        //],
      //},
      //{
        //object: 'block',
        //type: 'equation',
        //nodes: [
          //{
            //object: 'text',
            //leaves: [{
              //text: '\\int_0^\\infty x^2 dx',
            //}]
          //},
        //],
      //},
      //{
        //object: 'block',
        //type: 'image',
        //data: {
          //src:
            //'https://img.washingtonpost.com/wp-apps/imrs.php?src=https://img.washingtonpost.com/news/speaking-of-science/wp-content/uploads/sites/36/2015/10/as12-49-7278-1024x1024.jpg&w=1484'
        //}
      //},
    //],
  //},
//});

const algorithmDescription = Value.fromJSON({
  document: {
    nodes: [
      {
        object: 'block',
        type: 'paragraph',
        nodes: [
          {
            object: 'text',
            leaves: [
              {
                text: 'A line of text in a paragraph.',
              },
            ],
          },
        ],
      },
    ],
  },
});

const initialState = {
  algorithmDescription
};

export default function (state = initialState, action) {
  switch (action.type) {
    case actions.FETCH_ALGORITHM_DESCRIPTION_SUCCEEDED: {
      const { payload } = action;
      const document = Value.fromJSON({
        document: payload[0].scientific_theory.document
      });
      return { algorithmDescription: document };
    }

    default: return state;
  }
}
