import React from 'react';
import Example from '../component/Example';

// Functional component
const HomeKlur = () => {
  // Some state variable
  const [count, setCount] = React.useState(0);

  // Function to handle click event
  const handleClick = () => {
    setCount(count + 1);
  };

  return (
    <div>
      <h1>Functional Component Example Home klur</h1>
      <p>Count: {count}</p>
      <button onClick={handleClick}>Increment</button>
      <Example></Example>
    </div>
  );
};

export default HomeKlur;
