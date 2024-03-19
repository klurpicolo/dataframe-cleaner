import React from 'react';

// Functional component
const About = () => {
  // Some state variable
  const [count, setCount] = React.useState(0);

  // Function to handle click event
  const handleClick = () => {
    setCount(count + 1);
  };

  return (
    <div>
      <h1>Functional Component Example about</h1>
      <p>Count: {count}</p>
      <button onClick={handleClick}>Increment</button>
    </div>
  );
};

export default About;
