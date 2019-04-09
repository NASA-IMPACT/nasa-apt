/* global File */
import AWS from 'aws-sdk';
import uuid from 'uuid/v1';
import actions from '../constants/action_types';

const s3 = new AWS.S3({
  endpoint: 'http://localhost:4572',
  s3ForcePathStyle: true,
  region: 'us-east-1',
  accessKeyId: 'key',
  secretAccessKey: 'key'
});

const renameFile = (file, id) => {
  const extension = file.name.split('.').pop();
  const idFileName = `${id}.${extension}`;
  const idFile = new File([file], idFileName, { type: file.type });
  return idFile;
};

const uploadMiddleware = store => next => async (action) => {
  const { type, payload } = action;
  next(action);
  if (type === actions.UPLOAD_FILE) {
    try {
      const { file } = payload;
      const id = uuid();
      const keyedFile = renameFile(file, id);
      const key = keyedFile.name;
      const response = await s3.upload({
        Key: key,
        Body: keyedFile,
        Bucket: 'figures',
        ContentType: keyedFile.type
      }).promise();
      const { Location } = response;
      store.dispatch({
        type: actions.UPLOAD_FILE_SUCCESS,
        payload: Location
      });
    } catch (error) {
      store.dispatch({
        type: actions.UPLOAD_FILE_FAIL,
        payload: error
      });
    }
  }
  next(action);
};

export default uploadMiddleware;
