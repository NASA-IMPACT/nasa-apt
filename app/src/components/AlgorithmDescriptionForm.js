import { connect } from 'react-redux';
import { createAlgorithmDescription, fetchAlgorithmDescription } from '../actions/actions';
import FreeEditor from './FreeEditor';


const mapStateToProps = (state) => {
  const { algorithmDescription } = state.application;
  return { value: algorithmDescription };
};

const mapDispatchToProps = dispatch => ({
  createDocument: document => dispatch(createAlgorithmDescription(document)),
  fetchDocument: id => dispatch(fetchAlgorithmDescription(id))
});

export default connect(mapStateToProps, mapDispatchToProps)(FreeEditor);
