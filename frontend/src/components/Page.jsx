import React from 'react'
import Container from 'react-bootstrap/Container'




const Page = (props) => {

  const styles = {
    minHeight: 'auto',
    maxWidth: '80%',
    boxShadow: '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)',
    marginTop: '30px',
    marginBottom: '30px',
    paddingTop: '30px'
  }

  return (
    <Container fluid style={styles}>
      {props.children}
    </Container>
  )
}

export default Page