import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import {
  createAlgorithmImplementation,
  updateAlgorithmImplementation,
  deleteAlgorithmImplementation,

  createAccessInput,
  updateAccessInput,
  deleteAccessInput,

  createAccessOutput,
  updateAccessOutput,
  deleteAccessOutput,

  createAccessRelated,
  updateAccessRelated,
  deleteAccessRelated
} from '../actions/actions';
import {
  Inpage
} from './common/Inpage';
import EditPage from './common/EditPage';
import ImplementationForm from './ImplementationForm';

function AlgorithmImplementation(props) {
  const {
    atbdVersion
  } = props;
  let returnValue;
  if (atbdVersion) {
    const {
      atbd,
      t,
      createAlgorithmImplementation: createImplementation,
      updateAlgorithmImplementation: updateImplementation,
      deleteAlgorithmImplementation: delImplementation,

      createAccessInput: createInput,
      updateAccessInput: updateInput,
      deleteAccessInput: deleteInput,

      createAccessOutput: createOutput,
      updateAccessOutput: updateOutput,
      deleteAccessOutput: deleteOutput,

      createAccessRelated: createRelated,
      updateAccessRelated: updateRelated,
      deleteAccessRelated: deleteRelated

    } = props;

    const {
      title,
      atbd_id
    } = atbd;

    const {
      algorithm_implementations,
      data_access_input_data,
      data_access_output_data,
      data_access_related_urls
    } = atbdVersion;

    returnValue = (
      <Inpage>
        <EditPage
          title={title || ''}
          id={atbd_id}
          step={6}
        >
          <h2>Algorithm Implementation</h2>
          <ImplementationForm
            title="Algorithm Implementation"
            id="implementations-form"
            idProperty="algorithm_implementation_id"
            urlProperty="access_url"
            descriptionProperty="execution_description"
            data={algorithm_implementations}
            create={createImplementation}
            update={updateImplementation}
            del={delImplementation}
            t={{
              url: t.implementation_url,
              description: t.implementation_description
            }}
          />

          <ImplementationForm
            title="Data Access Input"
            id="data-access-input-form"
            idProperty="data_access_input_data_id"
            urlProperty="access_url"
            descriptionProperty="description"
            data={data_access_input_data}
            create={createInput}
            update={updateInput}
            del={deleteInput}
            t={{
              url: t.access_input_url,
              description: t.access_input_description
            }}
          />

          <ImplementationForm
            title="Data Access Output"
            id="data-access-output-form"
            idProperty="data_access_output_data_id"
            urlProperty="access_url"
            descriptionProperty="description"
            data={data_access_output_data}
            create={createOutput}
            update={updateOutput}
            del={deleteOutput}
            t={{
              url: t.access_output_url,
              description: t.access_output_description
            }}
          />

          <ImplementationForm
            title="Data Access Related URLs"
            id="data-access-related-form"
            idProperty="data_access_related_url_id"
            urlProperty="url"
            descriptionProperty="description"
            data={data_access_related_urls}
            create={createRelated}
            update={updateRelated}
            del={deleteRelated}
            t={{
              url: t.access_related_url,
              description: t.access_related_description
            }}
          />
        </EditPage>
      </Inpage>
    );
  } else {
    returnValue = <div>Loading</div>;
  }
  return returnValue;
}

AlgorithmImplementation.propTypes = {
  atbdVersion: PropTypes.object,
  atbd: PropTypes.object,
  t: PropTypes.object,
  createAlgorithmImplementation: PropTypes.func,
  updateAlgorithmImplementation: PropTypes.func,
  deleteAlgorithmImplementation: PropTypes.func,

  createAccessInput: PropTypes.func,
  updateAccessInput: PropTypes.func,
  deleteAccessInput: PropTypes.func,

  createAccessOutput: PropTypes.func,
  updateAccessOutput: PropTypes.func,
  deleteAccessOutput: PropTypes.func,

  createAccessRelated: PropTypes.func,
  updateAccessRelated: PropTypes.func,
  deleteAccessRelated: PropTypes.func
};

const mapStateToProps = (state) => {
  const { application: app } = state;
  const { atbdVersion, t } = app;
  const atbd = atbdVersion ? atbdVersion.atbd : {};
  return {
    atbdVersion,
    atbd,
    t: t ? t.algorithm_implementation : {}
  };
};

const mapDispatchToProps = {
  createAlgorithmImplementation,
  updateAlgorithmImplementation,
  deleteAlgorithmImplementation,

  createAccessInput,
  updateAccessInput,
  deleteAccessInput,

  createAccessOutput,
  updateAccessOutput,
  deleteAccessOutput,

  createAccessRelated,
  updateAccessRelated,
  deleteAccessRelated
};

export default connect(mapStateToProps, mapDispatchToProps)(AlgorithmImplementation);
