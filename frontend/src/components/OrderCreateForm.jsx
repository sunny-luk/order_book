import React, { useState } from 'react'
import PropTypes from 'prop-types'
import map from 'lodash/map'
import Form from 'react-bootstrap/Form'
import Button from 'react-bootstrap/Button'
import Modal from 'react-bootstrap/Modal'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import URLS from '../urls'
import makeRequest from '../services/api'

const OrderCreateForm = (props) => {

  const { show, setShow } = props

  const SIDE_CHOICES = {
    Buy: 1,
    Sell: -1
  }

  const [ formData, setFormData ] = useState({
    order_id: null,
    side: SIDE_CHOICES.Sell,
    price: 0.0
  })
  const [ loading, setLoading ] = useState(false)

  const onFieldChange = (fieldId, value) => {
    setFormData({...formData, [fieldId]: value})
  }

  const submitForm = (e) => {
    e.preventDefault()
    setLoading(true)
    makeRequest({
      method: 'POST',
      url: URLS.CREATE_ORDER,
      data: formData
    }).then(data => {
        onHide()
        alert(data.data.msg)
      }
    ).catch(err => {
      setLoading(false)
      alert(err.response.data.msg)
    })
  }

  const onHide = () => {
    setLoading(false)
    setShow(false)
  }

  return (
    <Modal show={show} onHide={onHide}>
      <Modal.Header>New Order</Modal.Header>
      <Modal.Body>
        <Form onSubmit={submitForm}>
        <Form.Group controlId='order_id'>
          <Form.Label>Order ID</Form.Label>
          <Form.Control type="text" placeholder="Enter order ID" onSelect={(e) => onFieldChange('order_id', e.target.value)}/>
          <Form.Text className="text-muted">
            Must be unique
          </Form.Text>
        </Form.Group>

        <Form.Group controlId="side">
          <Form.Label>Side</Form.Label>
          <Form.Control as="select" value={formData.side} onChange={(e) => {onFieldChange('side', Number(e.target.value))}}>
            {
              map(SIDE_CHOICES, (value, verbose) => {
                return (
                  <option key={verbose} value={value}>{verbose}</option>
                )
              })
            }
          </Form.Control>
        </Form.Group>
        <Form.Group controlId="quantity">
          <Form.Label>Quantity</Form.Label>
          <Form.Control type="text" placeholder="Enter quantity" onChange={(e) => onFieldChange('quantity', e.target.value)}/>
        </Form.Group>
        <Form.Group controlId="price">
          <Form.Label>Price</Form.Label>
          <Form.Control type="text" placeholder="Enter price" onChange={(e) => onFieldChange('price', e.target.value)}/>
        </Form.Group>
        <Row>
          <Col xs={12} md={{span: 6, offset: 3}} lg={{span: 4, offset: 4}}>
            <Button block variant="info" type="submit" disabled={loading}>
              { loading ? 'Submitting...' : 'Submit'} 
            </Button>
          </Col>
        </Row>
        
      </Form>
      </Modal.Body>
    </Modal>
  )

}

OrderCreateForm.propTypes = {
  show: PropTypes.bool.isRequired,
  setShow: PropTypes.func.isRequired
}

export default OrderCreateForm