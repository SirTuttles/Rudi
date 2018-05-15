from general import *
import os

class DatParser(object):
    def __init__(self):
        self.raws = {}
        self.compounds = []
        self.dat_paths = []

    def _isAttr(self, line):
        if len(line.split('=')) == 2:
            return True
        else:
            return False

    def _isHeader(self, line):
        line = line.strip()
        if isIn(line, '[', ']'):
            return True
        else:
            return False
        
    def _headerFromLine(self, line):
        return peel(line, '[', ']')
    
    def _attrFromLine(self, line):
        return [s.strip() for s in line.split('=')]
    
    def _isMultiLineValue(self, value):
        delim = '"'
        if value.strip().startswith(delim):
            return True
        else:
            return False
            
    def _handleValue(self, value, file=None):
        if self._isMultiLineValue(value):
            value = self._handleMultiLineValue(value, file)
        elif self._isListValue(value):
            value = self._handleListValue(value, file)
        else:
            value = toNum(value)
        return value
    
    def _isListValue(self, value):
        delim = '['
        if value.strip().startswith(delim):
            return True
        else:
            return False
        
    def _handleMultiLineValue(self, value, file=None):
        delim = '"'
        value = value.lstrip(delim)
        for i in range(len(value)):
            if value[i] == delim:
                return value[0:i]
                
        for line in file:
            value += '\n'
            for i in range(len(line)):
                if line[i] == delim:
                    return value + line[0:i]
            value += line
    
    def _handleListValue(self, value, file=None):
        # A list value is handled like a long value but
        # with the added stipulation 
        delim_open = '['
        delim_close = ']'
        delim_sep = ','
        esc_sep = '\\'
        vals = []
        
        whole_value = value
        if whole_value.find(delim_close) == -1:
            whole_value += '\n'
            for line in file:
                whole_value += line
                if line.find(delim_close) != -1:
                    break
        iroot = 1
        for i in range(len(whole_value)):
            if whole_value[i] == delim_sep and whole_value[i-1] != esc_sep:
                vals.append(whole_value[iroot:i])
                iroot = i + 1
            elif whole_value[i] == delim_close:
                vals.append(whole_value[iroot:i])
        vals = [val.strip() for val in vals]
 
        
        return vals
    
    def getDatNames(self):
        names = []
        for path in self.dat_paths:
            names.append(os.path.basename(path))
        return names
    
    def valFromStr(self, s):
        """A special use-case method intended
        to parse values from external sources."""
        if self._isMultiLineValue(s):
            value = self._handleMultiLineValue(s)
        elif self._isListValue(s):
            value = self._handleListValue(s)
        else:
            value = toNum(s)
        
        return value
    
    def read(self, *fpaths):
        failed = []
        header = 'global'
        for fpath in fpaths:
            try:
                with open(fpath) as file:
                    pass
            except FileNotFoundError:
                failed.append(fpath)
                continue
            
            with open(fpath) as file:

                for line in file:
                    line = line.strip()
                    
                    if self._isHeader(line):
                        header = self._headerFromLine(line)
                        self.raws[header] = {}
                    elif self._isAttr(line):
                        name, value = self._attrFromLine(line)
                        
                        value = self._handleValue(value, file)
                            
                        # Is there more than one attribute with this name?
                        if name in self.raws[header]:
                            # If so, convert it into a list
                            # and append to it from now on.
                            if name not in self.compounds:
                                self.compounds.append(name)
                                original_value = self.raws[header][name]
                                self.raws[header][name] = []
                                self.raws[header][name].append(original_value)
                            self.raws[header][name].append(value)
                        else:
                            self.raws[header][name] = value
        for fpath in fpaths:
            if fpath in failed:
                pass
            else:
                self.dat_paths.append(fpath)
        return failed
        
    def getDatPaths(self):
        return self.dat_paths
        
    def getRaws(self):
        return self.raws
    
    def getValue(self, header, name):
        return self.raws[header][name]
    
    def getGobs(self):
        gobs =[]
        for raw in self.raws:
            gobs.append(GameObject(raw, self.raws[raw]))
        return gobs
    
    def getGob(self, key):
        if key in self.raws:
            return GameObject(key, self.raws[key])
            
    def updateWithGob(self, gob):
        header = gob.getAttr('name')
        if header in self.raws:
            print(header, 'is in raws')
        for attr in gob.getAttributes():
            if attr == 'name':
                continue
            else:
                name = attr
                self.raws[header][name] = gob.getAttr(name)
                
    def updateValue(self, header, name, value):
        self.raws[header][name] = self._handleValue(value)
            
    def updateHeader(self, header, new_header):
        self.raws[new_header] = self.raws.pop[header]
            
    def addHeader(self, header):
        if header in self.raws:
            print('Header already exists!')
            return False
        
        self.raws[header] = {}
        
    def addName(self, header, name, value=''):
        if not header in self.raws:
            print('Header does not exist!')
            return False
        elif name in self.raws[header]:
            self.updateValue(header, name, value)
        
        self.raws[header][name] = self._handleValue(value)
            
    def save(self):
        for path in self.dat_paths:
            # Safety first! Backup current.
            with open(path + '.bak', 'w') as bak:
                with open(path, 'r') as cur:
                    bak.write(cur.read())
                    
            with open(path, 'w') as dat:
                for raw in self.raws:
                    dat.write('[%s]\n' % raw)
                    for name in self.raws[raw]:
                        value = self.raws[raw][name]
                        if isinstance(value, list):
                            value = '[%s]' % ','.join(value)
                        dat.write('%s = %s\n' % (name, value))
                    dat.write('\n\n')
    
    def delete(self, header):
        if header in self.raws:
            del(self.raws[header])
        self.save()
            
class GameObject(object):
    def __init__(self, name, attributes):
        self.name = name
        for attr in attributes:
            setattr(self, attr, attributes[attr])
            
    def getAttributes(self):
        return self.__dict__
        
    def getAttr(self, key):
        return getattr(self, key, False)
            
        
def main():
    datparser = DatParser()
    datparser.read('data/CONVERSATIONS.DAT')
    gobs = datparser.getGobs()
    print('Getting GOBs from  the following .DAT files: %s\n'
        % datparser.getDatNames())
    for gob in gobs:
        print('GOB: %s\n%s\n\n' % (gob.getAttr('name'), gob.getAttributes()))
        
if __name__ == '__main__':
    main()