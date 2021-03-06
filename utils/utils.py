import logging
import time
from datetime import datetime
from json import dumps
from typing import List, Optional, Union
from urllib.parse import ParseResult, parse_qsl, unquote, urlencode, urljoin, urlparse

import datadog
from django.contrib.sitemaps.views import sitemap, x_robots_tag
from django.core.paginator import Page, Paginator
from django.utils.timezone import now

from getpet import settings
from utils.models import PageInfoEntry, PaginationInfo

logger = logging.getLogger(__name__)


def try_parse_int(value) -> Optional[int]:
    if value:
        try:
            return int(value)
        except ValueError:
            return None


def django_now() -> datetime:
    return now()


class PageEntry(object):
    pass


class PageWithPageLink(Page):
    def __init__(self, page_link_function, object_list, number, paginator):
        self._page_link_function = page_link_function
        super().__init__(object_list, number, paginator)

    def previous_page_link(self):
        if self.has_previous():
            return self.page_link(self.previous_page_number())

    def next_page_link(self):
        if self.has_next():
            return self.page_link(self.next_page_number())

    def page_link(self, page_number):
        return self._page_link_function(page_number)

    def pagination_info(self) -> PaginationInfo:
        previous_url = self.page_link(self.previous_page_number()) if self.has_previous() else None
        next_url = self.page_link(self.next_page_number()) if self.has_next() else None

        entries = []
        skipped = False
        count = self.paginator.num_pages
        for i in range(1, count + 1):
            if self.number - 2 <= i <= self.number + 2 or i == 1 or i == count:
                if skipped:
                    skipped = False
                    entries.append(PageInfoEntry(text="...", url=None, is_active=False))

                entries.append(
                    PageInfoEntry(
                        text=str(i),
                        url=self.page_link(i) if self.number != i else None,
                        is_active=self.number == i)
                )
            else:
                skipped = True

        return PaginationInfo(
            previous_url=previous_url,
            next_url=next_url,
            entries=entries,
        )


class PaginatorWithPageLink(Paginator):
    def _get_page(self, *args, **kwargs):
        return PageWithPageLink(self._page_link_function, *args, **kwargs)

    def __init__(self, object_list, per_page, page_link_function, orphans=0, allow_empty_first_page=True):
        super().__init__(object_list, per_page, orphans, allow_empty_first_page)
        self._page_link_function = page_link_function


def add_url_params(url, params):
    """ Add GET params to provided URL being aware of existing.
    :param url: string of target URL
    :param params: dict containing requested params to be added
    :return: string with updated URL
    >> url = 'http://stackoverflow.com/test?answers=true'
    >> new_params = {'answers': False, 'data': ['some','values']}
    >> add_url_params(url, new_params)
    'http://stackoverflow.com/test?data=some&data=values&answers=false'
    """
    # Unquoting URL first so we don't loose existing args
    url = unquote(url)
    # Extracting url info
    parsed_url = urlparse(url)
    # Extracting URL arguments from parsed URL
    get_args = parsed_url.query
    # Converting URL arguments to dict
    parsed_get_args = dict(parse_qsl(get_args))
    # Merging URL arguments dict with new params
    parsed_get_args.update(params)

    parsed_get_args = {k: v for k, v in parsed_get_args.items() if v is not None}

    # Bool and Dict values should be converted to json-friendly values
    # you may throw this part away if you don't like it :)
    parsed_get_args.update(
        {k: dumps(v) for k, v in parsed_get_args.items()
         if isinstance(v, (bool, dict))}
    )

    # Converting URL argument to proper query string
    encoded_get_args = urlencode(parsed_get_args, doseq=True)
    # Creating new parsed result object based on provided with new
    # URL arguments. Same thing happens inside of urlparse.
    new_url = ParseResult(
        parsed_url.scheme, parsed_url.netloc, parsed_url.path,
        parsed_url.params, encoded_get_args, parsed_url.fragment
    ).geturl()

    return new_url


def find_first(seq, predicate, default=None):
    return next((x for x in seq if predicate(x)), default)


def file_extension(file_name: str) -> str:
    return file_name.split('.')[-1].lower()


def full_path(path: str) -> str:
    return urljoin(settings.BASE_DOMAIN, path)


@x_robots_tag
def sitemap_with_images(request, sitemaps, section=None, content_type='application/xml'):
    return sitemap(request, sitemaps, section, 'sitemap/sitemap.xml', content_type)


class Datadog:
    class __DatadogSingleton:
        def __init__(self):
            datadog.initialize(**settings.DATADOG_SETTINGS)

    instance = None

    def __init__(self):
        if not Datadog.instance:
            Datadog.instance = Datadog.__DatadogSingleton()

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def gauge(self, metric_name: str, value: Union[int, float], tags: Optional[List[str]] = None):
        options = {
            'metric': metric_name,
            'points': [(int(time.time()), value)],
            'type': 'gauge',
        }

        if tags:
            options['tags'] = tags

        return datadog.api.Metric.send(**options)
