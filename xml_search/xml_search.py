import os
import sys
import logging
import click
import click_log
from lxml import etree

log = logging.getLogger(__name__)
click_log.basic_config(log)


class XMLSearch(object):

    def __init__(
        self,
        xml_string,
        xpath_statement,
        explicit_xpath=False,
        primary_ns=None
    ):
        self.xml_string = xml_string

        self.explicit_xpath = explicit_xpath

        self.primary_ns = primary_ns
        self.namespaces = None
        self.process()

        if logging.getLogger().isEnabledFor(logging.DEBUG):
            if len(self.namespaces) > 0:
                log.debug("namespaces :")
                for k, v in self.namespaces.items():
                    log.debug("%5s : %s" % (k, v))

        if not self.primary_ns:
            if len(self.namespaces) > 0:
                self.primary_ns = next(iter(self.namespaces))

        log.debug("primary : %s" % self.primary_ns)

        if self.explicit_xpath:
            self.xpath_statement = xpath_statement
        else:
            if len(self.namespaces) > 0:
                self.xpath_statement = preprocess_path(
                    xpath_statement, self.primary_ns)
            else:
                self.xpath_statement = xpath_statement

    def process(self):
        try:
            # self.root = etree.fromstring(self.xml_string.encode('utf-8'))
            self.root = etree.fromstring(self.xml_string)
            self.namespaces = self.extract_namespaces(self.xml_string)
        except ValueError as ve:
            log.warning(ve)

    def extract_namespaces(self, xml_string):
        # return {k:v for k,v in self.root.nsmap.items() if k}
        product = {}
        if len(self.root.nsmap) == 0:
            return product

        for k, v in self.root.nsmap.items():
            key = None
            value = None
            if not k:
                key = 'bs'
                self.primary_ns = 'bs'
            else:
                key = k
            value = v

            product[key] = value

        return product

    def execute(self):
        log.debug('execute()')
        log.debug('xpath : %s' % self.xpath_statement)
        log.debug('ns    : %s' % self.namespaces)
        result = None
        try:
            if len(self.namespaces) > 0:
                result = self.root.xpath(
                    self.xpath_statement,
                    namespaces=self.namespaces)
            else:
                result = self.root.xpath(self.xpath_statement)
        except ValueError as ve:
            log.warning("%s : %s" % (ve, self.xpath_statement))

        return result

    def process_result(self, product, filename=None):
        # True or False, when the XPath expression has a boolean result
        # a float, when the XPath expression has a numeric result
        # a 'smart' string (as described below),
        # when the XPath expression has a string result.
        # a list of items,
        # XPath string results are 'smart' in that they provide a getparent()

        result = None
        if type(product).__name__ == 'list':
            result = []
            for item in product:
                if type(item).__name__ == '_ElementUnicodeResult':
                    result.append(item)

                elif type(item).__name__ == '_Element':
                    if len(item.getchildren()) > 0:
                        prod = etree.tostring(
                            item, pretty_print=True).decode("utf-8")
                        result.append(prod)
                    else:
                        result.append(item.text)

                else:
                    result.append(item)
        else:
            result = product

        return result

    def report(self, filename=None):
        product = self.execute()

        processed = self.process_result(product, filename=filename)
        # print(" ")
        # print(type(processed).__name__ )
        # print(processed)

        if type(processed).__name__ in 'list':
            if filename:
                click.secho('%s:' % filename, bold=True)
            for item in processed:
                click.echo(item)
        else:

            if filename:
                click.secho('%s:' % filename, bold=True)
            click.echo(processed)


def preprocess_path(path, ns_entry):
    '''
    Take plain xpath like /mods/titleInfo/title and process to use the ns_entry
    Something like this :
    /mods:mods/mods:titleInfo/mods:title

    Ignore attribute parts though

    /bs:mods/bs:identifier/bs:@type

    Should be
    /bs:mods/bs:identifier/@type
    '''

    parts = path.split('/')
    product_list = []

    for item in parts:
        if item:
            if item.startswith("@"):
                thing = item
            else:
                thing = "%s:%s" % (ns_entry, item)
            product_list.append(thing)

    product = "/".join(product_list)
    product2 = "/%s" % product
    return product2


@click.command()
@click.argument(
    'path',
    # required=False
)
@click.argument(
    'input',
    nargs=-1,
    type=click.File('rb'),
    # required=False
)
@click.option(
    '-x',
    '--explicit_xpath',
    help='use explicit namespaces, do not assume',
    is_flag=True,
)
@click.option(
    '-ns',
    '--namespace',
    help='primary namespace to employ',
    default=None
)
@click_log.simple_verbosity_option(log)
def cli(path, input, explicit_xpath, namespace):
    log.debug('cli')
    # input will be a tuple of files
    if len(input) == 1:
        xml_string = input[0].read()
        search = XMLSearch(xml_string, path, explicit_xpath, namespace)
        # product = search.execute()
        search.report()
    elif len(input) > 1:
        for item in input:
            # print(item)
            file_actual = os.path.basename(item.name)

            xml_string = item.read()
            search = XMLSearch(xml_string, path, explicit_xpath, namespace)
            search.report(filename=file_actual)


if __name__ == '__main__':
    cli()
