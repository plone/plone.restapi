from plone.batching.batch import Batch
from plone.restapi.deserializer import json_body
from urllib.parse import parse_qsl
from urllib.parse import urlencode


DEFAULT_BATCH_SIZE = 25


class HypermediaBatch:
    def __init__(self, request, results):
        self.request = request

        self.b_start = int(json_body(self.request).get("b_start", False)) or int(
            self.request.form.get("b_start", 0)
        )
        self.b_size = int(json_body(self.request).get("b_size", False)) or int(
            self.request.form.get("b_size", DEFAULT_BATCH_SIZE)
        )

        self.batch = Batch(results, self.b_size, self.b_start)

    def __iter__(self):
        """Iterate over items in current batch."""
        return iter(self.batch)

    @property
    def items_total(self):
        """Return the number of total items in underlying sequence."""
        return self.batch.sequence_length

    @property
    def canonical_url(self):
        """Return the canonical URL to the batched collection-like resource,
        preserving query string params, but stripping all batching related
        params from it.
        """
        url = self.request["ACTUAL_URL"]
        qs_params = parse_qsl(self.request["QUERY_STRING"])

        # Remove any batching / sorting related parameters.
        # Also take care to preserve list-like query string params.
        for key, value in qs_params[:]:
            if key in ("b_size", "b_start", "sort_on", "sort_order", "sort_limit"):
                qs_params.remove((key, value))

        qs = urlencode(qs_params)

        if qs_params:
            url = "?".join((url, qs))
        return url

    @property
    def current_batch_url(self):
        url = self.request["ACTUAL_URL"]
        qs = self.request["QUERY_STRING"]
        if qs:
            url = "?".join((url, qs))
        return url

    @property
    def links(self):
        """Get a dictionary with batching links."""
        # Don't provide batching links if resultset isn't batched
        if self.items_total <= self.b_size:
            return

        links = {}

        first = self._batch_for_page(1)
        last = self._batch_for_page(self.batch.lastpage)
        next = self.batch.next
        prev = self.batch.previous

        links["@id"] = self.current_batch_url
        links["first"] = self._url_for_batch(first)
        links["last"] = self._url_for_batch(last)

        if next:
            links["next"] = self._url_for_batch(next)

        if prev:
            links["prev"] = self._url_for_batch(prev)

        return links

    def _batch_for_page(self, pagenumber):
        """Return a new Batch object for the given pagenumber."""
        new_batch = Batch.fromPagenumber(
            self.batch._sequence, pagesize=self.b_size, pagenumber=pagenumber
        )
        return new_batch

    def _url_for_batch(self, batch):
        """Return URL that points to the given batch."""
        # Calculate the start for the new batch page.
        # Make sure we account for plone.batching's one-based indexing and
        # that the start never drops below zero
        new_start = max(0, batch.start - 1)
        url = self._url_with_params(params={"b_start": new_start})
        return url

    def _url_with_params(self, params):
        """Build an URL based on the actual URL of the current request URL
        and add or update some query string parameters in it.
        """
        url = self.request["ACTUAL_URL"]
        qs_params = parse_qsl(self.request["QUERY_STRING"], keep_blank_values=1)

        # Take care to preserve list-like query string arguments (same QS
        # param repeated multiple times). In other words, don't turn the
        # result of parse_qsl into a dict!

        # Drop params to be updated, then prepend new params in order
        qs_params = [x for x in qs_params if x[0] not in list(params)]
        qs_params = sorted(params.items()) + qs_params

        qs = urlencode(qs_params)

        if qs_params:
            url = "?".join((url, qs))
        return url
