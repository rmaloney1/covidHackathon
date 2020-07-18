import Board, { onDataChange } from 'react-trello';
import React, { useState, useEffect } from 'react';
import components from 'react-trello/dist/components';

export default function Tasks() {

const data = {
  lanes: [
    {
      id: 'lane1',
      title: 'Unassigned',
      //label: '2/2',
      cards: [
        {id: 'Card1', title: 'Jira Task 1', description: 'Fix frontend code', label: '30 mins'},
        {id: 'Card2', title: 'Jira Task 2', description: 'Connect to AWS', label: '5 mins', metadata: {sha: 'be312a1'}}
      ]
    },
    {
      id: 'lane2',
      title: 'Meeting Not Needed',
      //label: '0/0',
      cards: []
    },
    {
      id: 'lane3',
      title: 'Meeting Needed',
      //label: '0/0',
      cards: []
    }
  ]
}

//useState hook 
// d is going to be the current state at render 
// pass useState a function so it only is set at the very start 
// set data when we drag the cards over and then use this to call the API 
const [d, setData] = useState(data)

//send a request to the backend that 
// var newData = {};

newData = () => {
  console.log(d);
  return d;
}

useEffect(() => {
  // do something after the render 
  onDataChange(newData);
  //console.log(newData);
})

onCardMoveAcrossLanes(fromLaneId, toLaneId, cardId, index)


  return (
    <div>
      <Board data={d} />
    </div>
  );
}


// const data = {
//   lanes: [
//     {
//       id: 'lane1',
//       title: 'Planned Tasks',
//       label: '2/2',
//       cards: [
//         {id: 'Card1', title: 'Write Blog', description: 'Can AI make memes', label: '30 mins', draggable: false},
//         {id: 'Card2', title: 'Pay Rent', description: 'Transfer via NEFT', label: '5 mins', metadata: {sha: 'be312a1'}}
//       ]
//     },
//     {
//       id: 'lane2',
//       title: 'Completed',
//       label: '0/0',
//       cards: []
//     }
//   ]
// }

// export default class App extends React.Component {
//   render() {
//     return <Board data={data} />
//   }
// }
