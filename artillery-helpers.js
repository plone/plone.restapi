module.exports = {
  catchNewLocation: catchNewLocation,
  catchGoalItem: catchGoalItem,
};

function catchNewLocation(requestParams, response, context, ee, next) {
  response.headers.location
    ? (context.vars["newLocation"] = response.headers.location)
    : (context.vars["newLocation"] = undefined);
  return next();
}

function catchGoalItem(requestParams, response, context, ee, next) {
  JSON.parse(response.body).items[0]
    ? (context.vars["newGoalItem"] = JSON.parse(response.body).items[0]["@id"])
    : undefined;
  return next();
}
